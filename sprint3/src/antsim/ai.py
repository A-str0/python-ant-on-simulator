from __future__ import annotations

from typing import Protocol


class AIProvider(Protocol):
    name: str

    def complete(self, prompt: str) -> str:
        ...


class FallbackProvider:
    name = "off"

    def complete(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "эпитаф" in prompt_lower:
            return "Он жил коротко, ел спорно, в бильярде был вечен."
        if "матка" in prompt_lower:
            return "Матка сказала: мысль здравая, но голосование уже уточнено."
        return "Событие сгенерировано без LLM: муравьи посмотрели на ТЗ и пошли по кругу."


class TemplateAI:
    def __init__(self, mode: str = "off") -> None:
        self.mode = mode
        self.provider: AIProvider = FallbackProvider()
        self.tokens_spent = 0
        self.cache: dict[str, str] = {}
        self.last_request_tick = -10

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def ask(self, prompt: str, tick: int, force: bool = False) -> str:
        if not force and tick - self.last_request_tick < 5:
            return self.cache.get(prompt, "AI кэширует молчание, потому что токены не резиновые.")
        if prompt in self.cache:
            return self.cache[prompt]
        result = self.provider.complete(prompt)
        self.cache[prompt] = result
        self.last_request_tick = tick
        self.tokens_spent += max(1, len(prompt.split()) + len(result.split()))
        return result

    def event_text(self, colony_summary: str, tick: int) -> str:
        prompt = f"Сгенерируй событие для колонии: {colony_summary}"
        return self.ask(prompt, tick)

    def queen_dialog(self, question: str, tick: int) -> str:
        prompt = f"Матка отвечает на вопрос: {question}"
        return self.ask(prompt, tick, force=True)

    def epitaph(self, name: str, death_cause: str, tick: int) -> str:
        prompt = f"Эпитафия для муравья {name}. Причина смерти: {death_cause}"
        return self.ask(prompt, tick, force=True)
