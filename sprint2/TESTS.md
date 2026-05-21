# Sprint2 Test Suite Documentation

## Overview

The test suite for Sprint2 provides comprehensive coverage of both existing functionality and planned features described in README.md. Tests are organized by feature area and include markers for pending implementation.

## Test Statistics

- **Total Tests**: 60
- **Passing**: 42 ✅
- **Skipped**: 18 ⏭️ (pending feature implementation)
- **Execution Time**: ~0.03s

## Test Organization

### 1. test_ants.py (10 tests)
Tests for ant behavior and lifecycle.

**Passing Tests:**
- `test_harvester_characteristics` (6 parametrized) - Verify all Harvester stats are correct
- `test_harvester_life_period` - Verify ant lifespan mechanics
- `test_harvester_dies_after_life_period` - Verify death at exact age threshold
- `test_harvester_age_increments` - Verify age increases by 1 each tick

**Skipped Tests:**
- `test_play_billiards` - Feature not yet implemented

### 2. test_colony.py (22 tests)
Tests for Colony initialization, food management, and basic mechanics.

**Passing Tests:**
- `test_initialization` (16 parametrized)
  - Valid cases: colonies with 0-234 ants, 0-999 food
  - Invalid colony_id types (int, datetime)
  - Invalid ant_count types (string, float, complex)
  - Invalid food types (string, complex)
  - Negative values validation (ant_count, food)
- `test_simulation_food` (3 parametrized) - Food consumption simulation
- `test_food_never_negative_after_tick` - Food clamping to 0
- `test_food_stays_zero_when_insufficient` - Food boundaries

### 3. test_storage.py (5 tests)
Tests for save/load system.

**Passing Tests:**
- `test_save_colony` - Verify save creates JSON file
- `test_list_saves` - Verify saves can be listed
- `test_load_colony` - Verify roundtrip save/load
- `test_load_nonexistent_colony` - FileNotFoundError handling
- `test_load_nonexistent_json_file` - Error handling with explicit extension

### 4. test_sprint2_features.py (23 tests)
Tests for Sprint2 features from README.md requirements.

**Passing Tests (6):**
- `TestMultipleAntTypes::test_colony_with_single_ant_type` - Basic creation with Harvesters
- `TestSaveSystemEnhancements::test_colony_serialization_includes_all_ants` - All ants saved
- `TestFoodConsumption::test_food_consumed_each_tick` - Food deduction works
- `TestFoodConsumption::test_food_never_goes_negative` - Food protection
- `TestAntLifecycle::test_ant_dies_at_life_period` - Ant death mechanics
- `TestAntLifecycle::test_dead_ants_removed_from_colony` - Dead ant cleanup

**Skipped Tests (17) - Pending Implementation:**

**Sprint2 Requirement 2: Multiple Ant Types**
- `test_colony_creation_with_tailor_ants` - Asian Tailor ant support
- `test_colony_creation_with_reactive_ants` - Red Reactive ant support

**Sprint2 Requirement 3: BILYARD Characteristics**
- `test_ant_has_bilyard_stats` - Ants have Б.И.Л.Ь.Я.Р.Д. stats
- `test_bilyard_stats_bounded_0_to_10` - Stats cannot exceed 0-10
- `test_bilyard_stats_increase_through_training` - Stat progression

**Sprint2 Requirement 4: Rooms System**
- `test_colony_has_default_rooms` - Default rooms initialized
- `test_assign_ant_to_room` - Ant assignment mechanic
- `test_cannot_assign_dead_ant_to_room` - Dead ant validation

**Sprint2 Requirement 5: Characteristic Progression**
- `test_characteristic_increases_in_training_room` - Stat training
- `test_characteristic_cannot_exceed_10` - Stat caps

**Sprint2 Requirement 6: Random Events**
- `test_random_events_can_occur` - Event spawning
- `test_pheromone_death_spiral_event` - Specific event type

**Sprint2 Requirement 7: Voting System**
- `test_colony_can_hold_voting` - Voting mechanic
- `test_queen_can_override_voting` - Queen override

**Sprint2 Requirement 8: Save System Enhancements**
- `test_ant_can_have_multiple_statuses` - Status tracking
- `test_save_includes_ant_type` - Ant type preservation
- `test_save_includes_bilyard_characteristics` - Stats in save

## Validation Coverage

### Type Validation
- ✅ colony_id must be string
- ✅ ant_count must be integer (not bool)
- ✅ food must be integer (not bool)
- ✅ Rejects float, complex, datetime types
- ✅ Rejects string values

### Value Validation
- ✅ ant_count cannot be negative
- ✅ food cannot be negative (in __init__)
- ✅ food clamped to 0 in tick()

### Ant Lifecycle
- ✅ Ants start alive with age 0
- ✅ Age increases by 1 each tick
- ✅ Ants die at age >= life_period
- ✅ Dead ants removed from colony

### Food System
- ✅ Food consumed by ants each tick
- ✅ Food never goes below 0
- ✅ Food clamped to exactly 0 (not negative)
- ✅ Handles insufficient food scenarios

### Serialization
- ✅ Colony can be converted to dict
- ✅ All ants are included in serialization
- ✅ Colony can be restored from dict

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_colony.py -v
```

### Run specific test class:
```bash
pytest tests/test_sprint2_features.py::TestBILYARDCharacteristics -v
```

### Run only passing tests (exclude skipped):
```bash
pytest tests/ -v --ignore-glob='**/test_sprint2_features.py' -k 'not skip'
```

### Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## Feature Readiness

### Implemented Features ✅
- Colony creation and validation
- Ant lifecycle (birth, aging, death)
- Food consumption and management
- Basic serialization/deserialization
- Input validation (types and values)

### Pending Features ⏭️
- Multiple ant types (Harvesters, Tailors, Red Reactives, Explosive)
- BILYARD characteristic system (Б.И.Л.Ь.Я.Р.Д.)
- Rooms and room assignments
- Ant statuses (smells_like_dead, fermented, billiard_main, infected)
- Random events (6 types)
- Voting system and queen mechanics
- Enhanced save format with all state

## Notes

- Tests follow pytest conventions with fixtures in conftest.py
- Parametrized tests reduce code duplication
- Skipped tests serve as specifications for Sprint2 features
- All passing tests verify critical functionality
- Edge cases and boundary conditions are thoroughly tested

## References

- README.md - Sprint2 requirements specification
- test_plan.md - Original test planning document
- pytest.ini - Test configuration
