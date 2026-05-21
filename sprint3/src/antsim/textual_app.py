from __future__ import annotations

from pathlib import Path
from typing import Any

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from .ants import AntStatus, STAT_NAMES
from .charts import heatmap, line_chart, radar_stats
from .colony import Colony
from .logging_utils import write_log
from .storage import save_colony


VIEW_TITLES = {
    "dashboard": "Dashboard",
    "ants": "Муравьи",
    "rooms": "Комнаты",
    "charts": "Графики",
    "economy": "ANT/DeFi",
    "diplomacy": "Соседи",
    "campaign": "Кампания",
    "events": "События",
    "help": "Помощь",
}


class ColonyTuiApp(App[None]):
    """Cross-platform TUI powered by Textual/Rich."""

    CSS = """
    Screen {
        background: #101418;
        color: #e6edf3;
    }

    #root {
        height: 100%;
        padding: 0 1;
    }

    #top {
        height: 7;
        margin-bottom: 1;
    }

    #summary {
        width: 2fr;
        height: 100%;
    }

    #resources {
        width: 1fr;
        height: 100%;
    }

    #body {
        height: 1fr;
    }

    #sidebar {
        width: 34;
        margin-right: 1;
    }

    #main {
        width: 1fr;
    }

    #status {
        height: 3;
        margin-top: 1;
    }

    Static {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("space", "pause", "Pause"),
        Binding("right", "step", "Step"),
        Binding("1", "speed(1)", "x1"),
        Binding("2", "speed(2)", "x2"),
        Binding("3", "speed(3)", "x3"),
        Binding("4", "speed(4)", "x4"),
        Binding("5", "speed(5)", "x5"),
        Binding("6", "speed(6)", "x6"),
        Binding("7", "speed(7)", "x7"),
        Binding("8", "speed(8)", "x8"),
        Binding("9", "speed(9)", "x9"),
        Binding("d", "view('dashboard')", "Dash"),
        Binding("a", "view('ants')", "Ants"),
        Binding("o", "view('rooms')", "Rooms"),
        Binding("g", "view('charts')", "Charts"),
        Binding("e", "view('economy')", "Economy"),
        Binding("p", "view('diplomacy')", "Diplomacy"),
        Binding("c", "view('campaign')", "Campaign"),
        Binding("x", "view('events')", "Events"),
        Binding("h", "view('help')", "Help"),
        Binding("up", "move(-1)", "Up"),
        Binding("down", "move(1)", "Down"),
        Binding("[", "room_delta(-1)", "Room-"),
        Binding("]", "room_delta(1)", "Room+"),
        Binding("r", "assign", "Assign"),
        Binding("R", "mass_assign", "Mass"),
        Binding("v", "vote", "Vote"),
        Binding("s", "save", "Save"),
        Binding("G", "god", "God"),
        Binding("f", "force_event", "Event"),
        Binding("m", "mine", "Mine"),
        Binding("n", "nft", "NFT"),
        Binding("i", "ai", "AI"),
        Binding("t", "trade", "Trade"),
        Binding("w", "war", "War"),
        Binding("y", "peace", "Peace"),
        Binding("l", "liquidity", "LP"),
        Binding("b", "borrow", "Borrow"),
        Binding("k", "stake", "Stake"),
    ]

    def __init__(self, colony: Colony, save_dir: Path) -> None:
        super().__init__()
        self.colony = colony
        self.save_dir = save_dir
        self.active_view = "dashboard"
        self.selected_ant = 0
        self.selected_room = 0
        self.selected_neighbor = 0
        self.selected_mission = 0
        self.message = "TUI запущен. Муравьи пока делают вид, что это прод."

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="root"):
            with Horizontal(id="top"):
                yield Static(id="summary")
                yield Static(id="resources")
            with Horizontal(id="body"):
                yield Static(id="sidebar")
                yield Static(id="main")
            yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        write_log(f"Textual TUI mounted for {self.colony.id}", category="tui")
        self.set_interval(0.5, self._auto_tick)
        self.refresh_view()

    def _auto_tick(self) -> None:
        if not self.colony.paused:
            for _ in range(max(1, min(9, self.colony.tui_speed))):
                self.colony.tick()
        self.refresh_view()

    def refresh_view(self) -> None:
        self.query_one("#summary", Static).update(self._summary_panel())
        self.query_one("#resources", Static).update(self._resources_panel())
        self.query_one("#sidebar", Static).update(self._sidebar_panel())
        self.query_one("#main", Static).update(self._main_panel())
        self.query_one("#status", Static).update(self._status_panel())

    def action_pause(self) -> None:
        self.colony.paused = not self.colony.paused
        self.message = "Пауза" if self.colony.paused else "Симуляция продолжена"
        self.refresh_view()

    def action_step(self) -> None:
        self.colony.tick()
        self.message = "Один тик прожит. Возможно зря."
        self.refresh_view()

    def action_speed(self, speed: int) -> None:
        self.colony.tui_speed = max(1, min(9, int(speed)))
        self.message = f"Скорость x{self.colony.tui_speed}"
        self.refresh_view()

    def action_view(self, view_name: str) -> None:
        self.active_view = view_name
        self.message = f"Экран: {VIEW_TITLES.get(view_name, view_name)}"
        self.refresh_view()

    def action_move(self, delta: int) -> None:
        if self.active_view == "ants":
            total = max(1, len(self.colony.ants))
            self.selected_ant = (self.selected_ant + delta) % total
        elif self.active_view == "rooms":
            rooms = self._enabled_room_ids()
            self.selected_room = (self.selected_room + delta) % max(1, len(rooms))
        elif self.active_view == "diplomacy":
            total = max(1, len(self.colony.neighbors))
            self.selected_neighbor = (self.selected_neighbor + delta) % total
        elif self.active_view == "campaign":
            total = max(1, len(self.colony.campaign))
            self.selected_mission = (self.selected_mission + delta) % total
        else:
            self.selected_ant = (self.selected_ant + delta) % max(1, len(self.colony.ants))
        self.refresh_view()

    def action_room_delta(self, delta: int) -> None:
        rooms = self._enabled_room_ids()
        self.selected_room = (self.selected_room + delta) % max(1, len(rooms))
        self.message = f"Целевая комната: {self.colony.rooms[rooms[self.selected_room]].name}"
        self.refresh_view()

    def action_assign(self) -> None:
        if not self.colony.ants:
            self.message = "Некого назначать"
            return
        rooms = self._enabled_room_ids()
        ok = self.colony.assign_ant_to_room(self.selected_ant, rooms[self.selected_room])
        self.message = "Муравей назначен" if ok else "Назначение не удалось"
        self.refresh_view()

    def action_mass_assign(self) -> None:
        rooms = self._enabled_room_ids()
        count = self.colony.mass_assign(AntStatus.BILLIARD_MAIN, rooms[self.selected_room])
        self.message = f"billiard_main -> {self.colony.rooms[rooms[self.selected_room]].name}: {count}"
        self.refresh_view()

    def action_vote(self) -> None:
        result = self.colony.hold_voting("TUI: продолжать ли этот пиздец")
        self.message = f"Голосование: {result.final_decision}; проценты={sum(result.percentages.values())}%"
        self.refresh_view()

    def action_save(self) -> None:
        path = save_colony(self.colony, self.save_dir)
        self.message = f"Сохранено: {path.name}"
        write_log(f"TUI save action for {self.colony.id}", category="tui")
        self.refresh_view()

    def action_god(self) -> None:
        result = self.colony.god_mode("balagan")
        self.message = f"God Mode: {result}"
        self.refresh_view()

    def action_force_event(self) -> None:
        sequence = ["pheromone", "smell", "fermented", "fungus", "billiard", "radiation", "ufo"]
        event_type = sequence[self.colony.time % len(sequence)]
        self.message = f"Событие: {self.colony.force_event(event_type)}"
        self.refresh_view()

    def action_mine(self) -> None:
        self.colony.mine_antcoin()
        self.message = f"ANTCOIN mined: balance {self.colony.antcoin:.1f}"
        self.refresh_view()

    def action_nft(self) -> None:
        if self.selected_ant >= len(self.colony.ants):
            self.message = "Нет выбранного муравья"
            return
        if self.colony.antcoin < 50:
            self.colony.mine_antcoin(50 - self.colony.antcoin)
        nft_id = self.colony.mint_nft(self.selected_ant)
        self.message = f"NFT minted: {nft_id}" if nft_id else "NFT не отчеканился"
        self.refresh_view()

    def action_ai(self) -> None:
        self.message = self.colony.ai_queen_dialog("что делать с бильярдом и дедлайном?")
        self.refresh_view()

    def action_trade(self) -> None:
        neighbor = self.colony.neighbors[self.selected_neighbor]
        resource = neighbor.trade_bias if neighbor.trade_bias in self.colony.resources else "water"
        if self.colony.resources.get(resource, 0) < 10:
            resource = max(self.colony.resources, key=lambda key: self.colony.resources[key])
        ok = self.colony.trade_with_neighbor(self.selected_neighbor, resource, 10)
        self.message = "Торговля прошла" if ok else "Торговля не прошла"
        self.refresh_view()

    def action_war(self) -> None:
        self.message = self.colony.attack_neighbor(self.selected_neighbor)
        self.refresh_view()

    def action_peace(self) -> None:
        ok = self.colony.make_peace(self.selected_neighbor)
        self.message = "Мир подписан на листе" if ok else "Мир не купился"
        self.refresh_view()

    def action_liquidity(self) -> None:
        ok = self.colony.provide_liquidity("food", min(25, self.colony.resources["food"]))
        self.message = self.colony.defi["last_action"] if ok else "LP не получилось"
        self.refresh_view()

    def action_borrow(self) -> None:
        self.colony.take_ant_loan(25, ticks=30)
        self.message = self.colony.defi["last_action"]
        self.refresh_view()

    def action_stake(self) -> None:
        if self.colony.antcoin < 10:
            self.colony.mine_antcoin(10)
        self.colony.stake_ant(10)
        self.message = self.colony.defi["last_action"]
        self.refresh_view()

    def _summary_panel(self) -> Panel:
        mode = "[yellow]PAUSED[/]" if self.colony.paused else "[green]LIVE[/]"
        text = (
            f"[bold cyan]{self.colony.id}[/]\n"
            f"tick: [bold]{self.colony.time}[/]  speed: x{self.colony.tui_speed}  mode: {mode}\n"
            f"ants: [bold]{self.colony.get_alive_ants_count()}[/]/{len(self.colony.ants)}  "
            f"happiness: {self.colony.average_happiness():.1f}\n"
            f"view: [bold]{VIEW_TITLES.get(self.active_view, self.active_view)}[/]"
        )
        return Panel(text, title="Колония", border_style="cyan", box=box.ROUNDED)

    def _resources_panel(self) -> Panel:
        text = (
            f"food: [green]{self.colony.resources['food']}[/]\n"
            f"protein: [magenta]{self.colony.resources['protein']}[/]\n"
            f"water: [blue]{self.colony.resources['water']}[/]\n"
            f"ANT: [yellow]{self.colony.antcoin:.1f}[/]  price: ${self.colony.ant_price:.6f}"
        )
        return Panel(text, title="Ресурсы / ticker", border_style="green", box=box.ROUNDED)

    def _sidebar_panel(self) -> Panel:
        rooms = self._enabled_room_ids()
        room = self.colony.rooms[rooms[self.selected_room]]
        ant = self.colony.ants[self.selected_ant] if self.colony.ants else None
        items = [
            f"[bold]Текущий муравей[/]: #{self.selected_ant}",
            ant.display_name if ant else "нет",
            f"[bold]Целевая комната[/]: {room.name}",
            f"{len(room.ant_ids)}/{room.capacity}, defense={room.defense}",
            "",
            "[bold]Навигация[/]",
            "d dashboard, a ants, o rooms",
            "g charts, e economy, p diplomacy",
            "c campaign, x events, h help",
            "",
            "[bold]Действия[/]",
            "r assign, R mass, v vote",
            "f event, G balagan, s save",
        ]
        return Panel("\n".join(items), title="Пульт", border_style="blue", box=box.ROUNDED)

    def _main_panel(self) -> Panel:
        renderers = {
            "dashboard": self._render_dashboard,
            "ants": self._render_ants,
            "rooms": self._render_rooms,
            "charts": self._render_charts,
            "economy": self._render_economy,
            "diplomacy": self._render_diplomacy,
            "campaign": self._render_campaign,
            "events": self._render_events,
            "help": self._render_help,
        }
        content = renderers.get(self.active_view, self._render_dashboard)()
        return Panel(content, title=VIEW_TITLES.get(self.active_view, "TUI"), border_style="white", box=box.ROUNDED)

    def _status_panel(self) -> Panel:
        return Panel(
            Text(self.message, overflow="ellipsis"),
            title="status",
            border_style="yellow",
            box=box.ROUNDED,
        )

    def _render_dashboard(self) -> Any:
        history = self.colony.history
        top = Columns(
            [
                Panel(line_chart("food", [p["food"] for p in history]), title="food"),
                Panel(line_chart("pop", [p["population"] for p in history]), title="population"),
                Panel(line_chart("ANT", [p["antcoin"] for p in history]), title="antcoin"),
            ],
            equal=True,
        )
        return Group(
            top,
            Text(radar_stats(self.colony.get_alive_ants()), style="bold cyan"),
            Text(heatmap(self.colony.rooms), style="white"),
            self._event_table(limit=5),
        )

    def _render_ants(self) -> Table:
        table = Table(box=box.SIMPLE_HEAVY, expand=True)
        table.add_column("#", justify="right", width=4)
        table.add_column("name")
        table.add_column("room")
        table.add_column("hp", justify="right")
        table.add_column("happy", justify="right")
        table.add_column("stats")
        table.add_column("statuses")
        start = max(0, self.selected_ant - 8)
        for index, ant in enumerate(self.colony.ants[start : start + 18], start=start):
            marker = ">" if index == self.selected_ant else " "
            style = "bold cyan" if index == self.selected_ant else ""
            statuses = ", ".join(sorted(ant.statuses)) or "ok"
            stats = " ".join(f"{stat}{ant.stats.get(stat, 0)}" for stat in STAT_NAMES)
            table.add_row(
                f"{marker}{index}",
                ant.personal_name,
                ant.current_room or "-",
                str(ant.health),
                str(ant.happiness),
                stats,
                statuses,
                style=style,
            )
        return table

    def _render_rooms(self) -> Table:
        table = Table(box=box.SIMPLE_HEAVY, expand=True)
        table.add_column("#", justify="right", width=4)
        table.add_column("room")
        table.add_column("type")
        table.add_column("fill", justify="right")
        table.add_column("def", justify="right")
        table.add_column("effect")
        rooms = self._enabled_room_ids()
        for index, room_id in enumerate(rooms):
            room = self.colony.rooms[room_id]
            marker = ">" if index == self.selected_room else " "
            style = "bold green" if index == self.selected_room else ""
            effect = {
                "server_room": "mine ANT",
                "billiard_room": "billiard/addiction",
                "mushroom_startup": "fungus/food",
                "trade_floor": "market",
                "hammock_room": "lazy reserve",
            }.get(room.type, room.type)
            table.add_row(
                f"{marker}{index}",
                room.name,
                room.type,
                f"{len(room.ant_ids)}/{room.capacity}",
                str(room.defense),
                effect,
                style=style,
            )
        return table

    def _render_charts(self) -> Text:
        history = self.colony.history
        lines = [
            line_chart("Food stock", [p["food"] for p in history], width=70),
            line_chart("Protein", [p["protein"] for p in history], width=70),
            line_chart("Water", [p["water"] for p in history], width=70),
            line_chart("Population", [p["population"] for p in history], width=70),
            line_chart("ANTCOIN", [p["antcoin"] for p in history], width=70),
            "",
            radar_stats(self.colony.get_alive_ants()),
            "",
            heatmap(self.colony.rooms),
        ]
        return Text("\n".join(lines))

    def _render_economy(self) -> Group:
        rates = Table(title="Market / DeFi", box=box.SIMPLE, expand=True)
        rates.add_column("metric")
        rates.add_column("value")
        rates.add_row("BTC", f"${self.colony.btc_price:,.2f}")
        rates.add_row("ANT price", f"${self.colony.ant_price:.6f}")
        rates.add_row("ANT balance", f"{self.colony.antcoin:.2f}")
        rates.add_row("ANT classic", f"{self.colony.antcoin_classic:.2f}")
        rates.add_row("staked", f"{self.colony.defi.get('staked_ant', 0):.2f}")
        rates.add_row("loans", str(len(self.colony.defi.get("loans", []))))
        rates.add_row("last", str(self.colony.defi.get("last_action", "-")))

        liquidity = Table(title="Liquidity", box=box.SIMPLE, expand=True)
        liquidity.add_column("pool")
        liquidity.add_column("amount", justify="right")
        for key, value in self.colony.defi["liquidity"].items():
            liquidity.add_row(key, f"{float(value):.1f}")

        return Group(
            rates,
            liquidity,
            Text("m mine | l provide liquidity | b borrow | k stake | n mint NFT", style="yellow"),
        )

    def _render_diplomacy(self) -> Group:
        table = Table(title="Neighbor colonies", box=box.SIMPLE_HEAVY, expand=True)
        table.add_column("#")
        table.add_column("name")
        table.add_column("attitude")
        table.add_column("strength")
        table.add_column("ideology")
        table.add_column("last action")
        for index, neighbor in enumerate(self.colony.neighbors):
            marker = ">" if index == self.selected_neighbor else " "
            style = "bold cyan" if index == self.selected_neighbor else ""
            table.add_row(
                f"{marker}{index}",
                neighbor.name,
                str(neighbor.attitude),
                str(neighbor.strength),
                neighbor.ideology,
                neighbor.last_action,
                style=style,
            )
        return Group(table, Text("t trade preferred resource | w war | y peace", style="yellow"))

    def _render_campaign(self) -> Table:
        table = Table(title="Story Campaign", box=box.SIMPLE_HEAVY, expand=True)
        table.add_column("#")
        table.add_column("mission")
        table.add_column("progress")
        table.add_column("reward")
        for index, mission in enumerate(self.colony.campaign):
            marker = ">" if index == self.selected_mission else " "
            style = "bold green" if mission.completed else ("bold cyan" if index == self.selected_mission else "")
            progress = ", ".join(
                f"{key}:{mission.progress.get(key, 0)}/{value}"
                for key, value in mission.goals.items()
            )
            table.add_row(f"{marker}{mission.id}", mission.title, progress, mission.reward, style=style)
        return table

    def _render_events(self) -> Group:
        return Group(
            self._event_table(limit=12),
            Text("\nПоследние события:\n" + "\n".join(self.colony.event_log[-12:])),
        )

    def _render_help(self) -> Text:
        return Text(
            "\n".join(
                [
                    "Space pause, Right single tick, 1-9 simulation speed",
                    "d/a/o/g/e/p/c/x/h switch screens",
                    "Up/Down select row, [/] select target room",
                    "r assign selected ant to target room",
                    "R send billiard_main ants to target room",
                    "v vote, f force event, G God balagan, s save",
                    "m mine ANT, n mint NFT, l liquidity, b borrow, k stake",
                    "t trade with selected neighbor, w attack, y peace",
                    "i ask AI-off queen dialogue",
                    "q quit",
                ]
            ),
            style="white",
        )

    def _event_table(self, limit: int) -> Table:
        table = Table(box=box.SIMPLE, expand=True)
        table.add_column("event")
        table.add_column("left", justify="right")
        table.add_column("description")
        if not self.colony.active_events:
            table.add_row("тихо", "-", "слишком тихо")
            return table
        for event in self.colony.active_events[:limit]:
            table.add_row(event.name, str(event.ticks_left), event.description)
        return table

    def _enabled_room_ids(self) -> list[str]:
        return [room_id for room_id, room in self.colony.rooms.items() if room.enabled]


def run_textual_tui(colony: Colony, save_dir: Path) -> None:
    ColonyTuiApp(colony, save_dir).run()
