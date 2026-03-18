
"""
Tests for execute_dice_sequence() — simulates complete dice turns
with scripted roll results and scripted movement choices.

Run:
    cd backend/app && python test_dice_sequence.py
    cd backend/app && python -m pytest test_dice_sequence.py -v
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from enums import Tires, Weather
from track import Track
from driver import Driver
from dice import (
    Dice,
    StepAction,
    DiceSequence,
    create_dice,
    resolve_turn,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_driver(
    tile_idx: int = 0,
    lane_idx: int = 1,
    square_idx: int = 0,
    gear: str = "0",
) -> Driver:
    d = Driver("TestDriver", "TestTeam", Tires.NORMAL, Weather.DRY)
    d.tile_idx = tile_idx
    d.lane_idx = lane_idx
    d.square_idx = square_idx
    d.current_gear = gear
    return d


def make_dices() -> Dict[str, Dice]:
    return {face: create_dice(face) for face in ("1", "2", "3", "4", "5", "6", "C", "B")}


def snapshot(driver: Driver) -> Dict[str, Any]:
    return {
        "tile_idx": driver.tile_idx,
        "lane_idx": driver.lane_idx,
        "square_idx": driver.square_idx,
        "current_gear": driver.current_gear,
    }


def scripted_rolls(results: List[str]):
    """Return a roll_provider that yields results from a list in order.

    Each call pops the next result. If the list runs out, falls back to
    returning the symbol itself (i.e. a 'safe' roll).
    """
    remaining = list(results)

    def provider(symbol: str, dices: Dict[str, Dice]) -> str:
        if remaining:
            return remaining.pop(0)
        return symbol  # safe fallback

    return provider


def scripted_actions(actions: List[StepAction]):
    """Return an action_provider that yields StepActions from a list in order.

    Falls back to 'move forward same lane' if the list runs out.
    """
    remaining = list(actions)

    def provider(step_index: int, driver: Driver, track: Track, gear: str) -> StepAction:
        if remaining:
            return remaining.pop(0)
        return StepAction(choice=1)

    return provider


def always_forward(step_index: int, driver: Driver, track: Track, gear: str) -> StepAction:
    """Simple action provider: always move forward, same lane."""
    return StepAction(choice=1)


# ── Tests ────────────────────────────────────────────────────────────────────

def test_simple_three_dice_no_warnings():
    """Sequence '3,4,5' with all safe rolls — driver moves 3 squares, no crashes."""
    track = Track("Albert Park")
    driver = make_driver(tile_idx=0, lane_idx=1, square_idx=0, gear="0")
    dices = make_dices()

    # Script rolls: each die lands on its own number (safe)
    rolls = scripted_rolls(['3', '4', '5'])

    result = resolve_turn(
        seq=['3', '4', '5'],
        dices=dices,
        driver=driver,
        track=track,
        actions=always_forward,
        roll_provider=rolls,
    )

    print(f"\n[test_simple_three_dice_no_warnings]")
    print(f"  final position: {snapshot(driver)}")
    print(f"  crash: {result.crash}")
    print(f"  final_gear: {result.final_gear}")
    print(f"  lost_control: {result.lost_control}")
    for s in result.steps:
        print(f"    step {s['step']}: {s['symbol']} -> {s['result']}, "
              f"pos {s['position_before']} -> {s['position_after']}, "
              f"crash {s['crash_before']}->{s['crash_after']}")

    assert result.crash == 0, f"Expected 0 crashes, got {result.crash}"
    assert result.lost_control is False
    assert len(result.steps) == 3, f"Expected 3 steps, got {len(result.steps)}"
    # Started at tile 0, lane 1, square 0 with 3 squares in tile 1.
    # After 3 moves forward: should have crossed into tile 2.
    assert driver.tile_idx >= 1, f"Expected to advance past tile 0, at tile_idx={driver.tile_idx}"


def test_two_dice_with_one_warning():
    """Sequence '3,4' where the first roll is a warning — crash should be 1."""
    track = Track("Albert Park")
    driver = make_driver(tile_idx=0, lane_idx=1, square_idx=0, gear="0")
    dices = make_dices()

    # First die: warning, second die: safe
    rolls = scripted_rolls(['⚠️', '4'])

    result = resolve_turn(
        seq=['3', '4'],
        dices=dices,
        driver=driver,
        track=track,
        actions=always_forward,
        roll_provider=rolls,
    )

    print(f"\n[test_two_dice_with_one_warning]")
    print(f"  final position: {snapshot(driver)}")
    print(f"  crash: {result.crash}")
    for s in result.steps:
        print(f"    step {s['step']}: {s['symbol']} -> {s['result']}, "
              f"crash {s['crash_before']}->{s['crash_after']}")

    assert result.crash == 1, f"Expected 1 crash, got {result.crash}"
    assert result.lost_control is False


def test_three_warnings_causes_loss_of_control():
    """Sequence '3,4,5' where all three roll warnings — triggers loss of control."""
    track = Track("Albert Park")
    driver = make_driver(tile_idx=0, lane_idx=1, square_idx=0, gear="0")
    dices = make_dices()

    rolls = scripted_rolls(['⚠️', '⚠️', '⚠️'])

    result = resolve_turn(
        seq=['3', '4', '5'],
        dices=dices,
        driver=driver,
        track=track,
        actions=always_forward,
        roll_provider=rolls,
    )

    print(f"\n[test_three_warnings_causes_loss_of_control]")
    print(f"  final position: {snapshot(driver)}")
    print(f"  crash: {result.crash}")
    print(f"  lost_control: {result.lost_control}")
    print(f"  final_gear: {result.final_gear}")

    assert result.lost_control is True, "Should have lost control"
    assert result.crash >= 3


def test_sequence_with_lane_change():
    """Sequence '2,3' where step 0 changes lane, step 1 moves forward."""
    track = Track("Albert Park")
    driver = make_driver(tile_idx=0, lane_idx=1, square_idx=0, gear="0")
    dices = make_dices()

    rolls = scripted_rolls(['2', '3'])
    actions = scripted_actions([
        StepAction(choice=2, new_lane=2),  # step 0: change to lane 2 then move
        StepAction(choice=1),              # step 1: move forward same lane
    ])

    result = resolve_turn(
        seq=['2', '3'],
        dices=dices,
        driver=driver,
        track=track,
        actions=actions,
        roll_provider=rolls,
    )

    print(f"\n[test_sequence_with_lane_change]")
    print(f"  final position: {snapshot(driver)}")
    print(f"  crash: {result.crash}")
    for s in result.steps:
        print(f"    step {s['step']}: {s['symbol']} -> {s['result']}, "
              f"action={s['action']}, "
              f"pos {s['position_before']} -> {s['position_after']}")

    assert driver.lane_idx == 2, f"Expected lane 2, got {driver.lane_idx}"
    assert result.crash == 0


def test_high_gear_into_restricted_square():
    """Sequence '4,5' starting near a max_gear=2 square — should trigger crash."""
    track = Track("Albert Park")
    # Tile 4 (index 3), lane 3, square 0.
    # Square 1 in lane 3 has max_gear: 2.
    # Rolling gear '5' into it should cause crash += 3.
    driver = make_driver(tile_idx=3, lane_idx=3, square_idx=0, gear="0")
    dices = make_dices()

    # Both rolls safe (land on their number)
    rolls = scripted_rolls(['4', '5'])

    result = resolve_turn(
        seq=['4', '5'],
        dices=dices,
        driver=driver,
        track=track,
        actions=always_forward,
        roll_provider=rolls,
    )

    print(f"\n[test_high_gear_into_restricted_square]")
    print(f"  final position: {snapshot(driver)}")
    print(f"  crash: {result.crash}")
    print(f"  lost_control: {result.lost_control}")
    for s in result.steps:
        print(f"    step {s['step']}: {s['symbol']} -> {s['result']}, "
              f"crash {s['crash_before']}->{s['crash_after']}")

    # First move (gear 4) into max_gear=2 square: crash += 3 -> lost control
    assert result.crash >= 3, f"Expected crash >= 3 from max_gear violation, got {result.crash}"


def test_coast_die_resolves_gear():
    """Sequence '3,C' — coast die should resolve to the previous gear."""
    track = Track("Albert Park")
    driver = make_driver(tile_idx=0, lane_idx=2, square_idx=0, gear="0")
    dices = make_dices()

    # '3' rolls safe, 'C' rolls coast symbol (⬜️)
    rolls = scripted_rolls(['3', '⬜️'])

    result = resolve_turn(
        seq=['3', 'C'],
        dices=dices,
        driver=driver,
        track=track,
        actions=always_forward,
        roll_provider=rolls,
    )

    print(f"\n[test_coast_die_resolves_gear]")
    print(f"  final position: {snapshot(driver)}")
    print(f"  final_gear: {result.final_gear}")
    print(f"  crash: {result.crash}")
    for s in result.steps:
        print(f"    step {s['step']}: {s['symbol']} -> {s['result']}, "
              f"resolved={s['gear']}")

    assert result.crash == 0


def test_single_die():
    """Sequence with just '2' — simplest possible turn."""
    track = Track("Albert Park")
    driver = make_driver(tile_idx=0, lane_idx=1, square_idx=0, gear="0")
    dices = make_dices()

    rolls = scripted_rolls(['2'])

    result = resolve_turn(
        seq=['2'],
        dices=dices,
        driver=driver,
        track=track,
        actions=always_forward,
        roll_provider=rolls,
    )

    print(f"\n[test_single_die]")
    print(f"  final position: {snapshot(driver)}")
    print(f"  crash: {result.crash}")

    assert result.crash == 0
    assert driver.square_idx == 1, f"Expected square 1, got {driver.square_idx}"


def test_warnings_accumulate_across_steps():
    """Sequence '2,3,4' with warnings on steps 0 and 2 — crash should be 2."""
    track = Track("Albert Park")
    driver = make_driver(tile_idx=0, lane_idx=2, square_idx=0, gear="0")
    dices = make_dices()

    # Step 0: warning, step 1: safe, step 2: warning
    rolls = scripted_rolls(['⚠️', '3', '⚠️'])

    result = resolve_turn(
        seq=['2', '3', '4'],
        dices=dices,
        driver=driver,
        track=track,
        actions=always_forward,
        roll_provider=rolls,
    )

    print(f"\n[test_warnings_accumulate_across_steps]")
    print(f"  crash: {result.crash}")
    print(f"  lost_control: {result.lost_control}")
    for s in result.steps:
        print(f"    step {s['step']}: {s['symbol']} -> {s['result']}, "
              f"crash {s['crash_before']}->{s['crash_after']}")

    assert result.crash == 2, f"Expected 2 crashes, got {result.crash}"
    assert result.lost_control is False


# ── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_simple_three_dice_no_warnings,
        test_two_dice_with_one_warning,
        test_three_warnings_causes_loss_of_control,
        test_sequence_with_lane_change,
        test_high_gear_into_restricted_square,
        test_coast_die_resolves_gear,
        test_single_die,
        test_warnings_accumulate_across_steps,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  ✅ PASSED")
        except AssertionError as e:
            failed += 1
            print(f"  ❌ FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"  ❌ ERROR: {type(e).__name__}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    print(f"{'='*60}")