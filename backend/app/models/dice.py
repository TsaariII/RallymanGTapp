from __future__ import annotations
import random
from typing import Dict, List, Callable, Optional, Tuple
from dataclasses import dataclass, field
from driver import Driver, do_movement
from track import Track


class Dice:
    def __init__(self, sides: List[str]) -> None:
        self.sides = sides

    def roll(self) -> str:
        if not self.sides:
            return 'Invalid dice!'
        return random.choice(self.sides)


DICE_FACES: Dict[str, List[str]] = {
    '1': ['1', '1', '1', '1', '1', '⚠️'],
    '2': ['2', '2', '2', '2', '2', '⚠️'],
    '3': ['3', '3', '3', '3', '⚠️', '⚠️'],
    '4': ['4', '4', '4', '4', '⚠️', '⚠️'],
    '5': ['5', '5', '5', '5', '⚠️', '⚠️'],
    '6': ['6', '6', '6', '6', '⚠️', '⚠️'],
    'C': ['⬜️', '⬜️', '⬜️', '⬜️', '⬜️', '⚠️'],
    'B': ['🟥', '🟥', '🟥', '🟥', '⚠️', '⚠️']
}


def create_dice(type: str) -> Dice:
    '''Create a single dice of a given type.'''
    return Dice(DICE_FACES.get(type, []))


def coast_or_brake(driver: Driver, seq: List[str], gear: str) -> str:
    """
    Resolve final gear when the last symbol is coast (C) or brake (B).
    """
    if gear == 'C':
        if seq and seq[0] == 'C':
            return driver.current_gear
    for i, symbol in enumerate(seq):
        if symbol == 'C' and i > 0:
            return seq[i - 1]
    if gear == 'B':
        i = 0
        while 1 < len(seq):
            if seq[i] == 'B':
                j = i
                while j + 1 < len(seq) and seq[j + 1] == 'B':
                    j += 1
                if j + 1 < len(seq):
                    return seq[j + 1]
                break
            i += 1
    return gear


# ── Action / roll abstractions ───────────────────────────────────────────


@dataclass
class StepAction:
    """Describes what the driver does for a single movement step.

    choice: 1 = move forward same lane, 2 = change lane then move forward
    new_lane: required when choice == 2
    """
    choice: int = 1
    new_lane: Optional[int] = None


MoveDecider = Callable[[int, Driver, Track, str], StepAction]

RollProvider = Callable[[str, Dict[str, Dice]], str]


def random_roll(symbol: str, dices: Dict[str, Dice]) -> str:
    """Default roll provider: use the actual dice."""
    return dices[symbol].roll()


def prompt_move_action(index: int, driver: Driver, track: Track, gear: str) -> StepAction:
    """CLI-only move decider. Uses input() — not called from web path."""
    while True:
        try:
            choice = int(
                input('Choose action (1: move forward same lane, 2: move forward change lane): ')
            )
        except ValueError:
            print('Invalid action! Try again')
            continue
        if choice in (1, 2):
            break
        print('Invalid action! Try again')
    new_lane = None
    if choice == 2:
        tile = track.tile(driver.tile_idx)
        while True:
            try:
                new_lane = int(input('Enter lane change number (1, 2, 3): '))
            except ValueError:
                print('Invalid lane change input! Try again.')
                continue
            if 1 <= new_lane <= tile.lanes:
                break
            print("Invalid lane! Try again.")
    return StepAction(choice=choice, new_lane=new_lane)


# ── Dice sequence result ─────────────────────────────────────────────────


@dataclass
class DiceSequence:
    """Everything that happens during one dice sequence execution."""
    crash: int = 0
    final_gear: str = ''
    lost_control: bool = False
    stopped_early: bool = False
    steps: List[Dict] = field(default_factory=list)


# Called after each step (except the last) to ask "keep going?"
# Receives (step_index, driver, DiceSequence-so-far).
# Returns True to continue, False to stop the sequence early.
ContinueDecider = Callable[[int, Driver, DiceSequence], bool]


def always_continue(step_index: int, driver: Driver, result: DiceSequence) -> bool:
    """Default continue decider: never stop early."""
    return True


def prompt_continue(step_index: int, driver: Driver, result: DiceSequence) -> bool:
    """CLI continue decider: let the player choose to stop mid-sequence."""
    choice = input(
        'Press Enter to continue or type exit to return to dice selection: '
    ).strip()
    return choice != 'exit'


# ── Core turn resolution ─────────────────────────────────────────────────


def resolve_turn(
    seq: List[str],
    dices: Dict[str, Dice],
    driver: Driver,
    track: Track,
    actions: MoveDecider,
    roll_provider: RollProvider = random_roll,
    continue_decider: ContinueDecider = always_continue,
) -> DiceSequence:
    """Execute a full dice sequence for one driver's turn.

    This is pure logic — no input() or print() calls.
    All outcomes are recorded in the returned DiceSequence.

    Args:
        seq:              list of dice symbols, e.g. ['3', '4', 'C']
        dices:            dict of symbol -> Dice objects
        driver:           the Driver taking the turn (mutated in place)
        track:            the Track
        actions:          callable that decides movement per step
        roll_provider:    callable that rolls a die (injectable for tests)
        continue_decider: callable asked after each step (except last)
                          whether to keep going. Returns False to stop early.

    Returns:
        DiceSequence with crash count, final gear, lost_control flag,
        stopped_early flag, and a step-by-step log in .steps
    """
    result = DiceSequence()
    crash = 0
    gear = ''
    breaks: List[str] = []

    for index, symbol in enumerate(seq):
        log: Dict = {
            'step': index,
            'symbol': symbol,
            'result': None,
            'gear': None,
            'action': None,
            'crash_before': crash,
            'crash_after': None,
            'pos_before': {
                'tile_idx': driver.tile_idx,
                'lane_idx': driver.lane_idx,
                'sqr_idx': driver.square_idx,
            },
            'pos_after': None,
            'brake_rolls': [],
        }
        if symbol == 'B':
            breaks.append('B')
            log['result'] = 'deferred_brake'
            log['crash_after'] = crash
            log['pos_after'] = {
                'tile_idx': driver.tile_idx,
                'lane_idx': driver.lane_idx,
                'sqr_idx': driver.square_idx,
            }
            result.steps.append(log)
            continue
        for _ in breaks:
            b_res = roll_provider('B', dices)
            log['brake_rolls'].append(b_res)
            if b_res == '⚠️':
                crash += 1
        breaks.clear()
        roll_result = roll_provider(symbol, dices)
        log['result'] = roll_result

        if roll_result == '⚠️':
            crash += 1
            resolved = symbol
        elif roll_result in {'⬜️', '🟥'}:
            resolved = coast_or_brake(driver, seq, roll_result)
        else:
            resolved = roll_result

        log['gear'] = resolved
        if crash >= 3:
            result.lost_control = True
            result.crash = crash

            final_gear = resolved
            if gear in {'C', 'B'}:
                final_gear = coast_or_brake(driver, seq, final_gear)
            result.final_gear = final_gear

            tile_color = track.tile(driver.tile_idx).color
            driver.stats.add_crash_tokens(gear, tile_color)

            try:
                num = int(final_gear)
            except ValueError:
                num = 0
            penalty_gear = '00' if num >= 3 else '0'
            driver.current_gear = penalty_gear

            log['crash_after'] = crash
            log['pos_after'] = {
                'tile_idx': driver.tile_idx,
                'lane_idx': driver.lane_idx,
                'sqr_idx': driver.square_idx,
            }
            result.steps.append(log)
            return result
        action = actions(index, driver, track, resolved)
        log['action'] = {'choice': action.choice, 'new_lane': action.new_lane}
        crash = do_movement(track, driver, crash, resolved, action.choice, action.new_lane)
        log['crash_after'] = crash
        log['pos_after'] = {
            'tile_idx': driver.tile_idx,
            'lane_idx': driver.lane_idx,
            'sqr_idx': driver.square_idx,
        }
        result.steps.append(log)
        if seq and seq[-1] == 'C':
            gear = coast_or_brake(driver, seq, resolved)
        else:
            gear = symbol
        driver.current_gear = gear
        if symbol != seq[-1]:
            if not continue_decider(index, driver, result):
                result.stopped_early = True
                result.crash = crash
                result.final_gear = driver.current_gear
                return result

    result.crash = crash
    result.final_gear = driver.current_gear
    print(f"Final gear: {driver.current_gear}")
    return result

@dataclass
class AllAtOnceResult:
    """Result of rolling all dice at once before moving."""
    rolls: List[Dict] = field(default_factory=list)
    crash: int = 0
    lost_control: bool = False
    moves: int = 0
    focus_tokens: int = 0
    final_gear: str = ''
    penalty_gear: Optional[str] = None


def all_at_once(
    seq: List[str],
    dices: Dict[str, Dice],
    driver: Driver,
    track: Track,
    roll_provider: RollProvider = random_roll,
) -> AllAtOnceResult:
    """Roll all dice first, then let the caller handle movement.

    In all-at-once mode, the player rolls every die before making any
    movement decisions. This function handles the rolling phase and
    returns the results. The caller (CLI or API) is responsible for
    collecting movement choices and applying them.

    Args:
        seq:            list of dice symbols
        dices:          dice lookup
        driver:         the Driver (gear/stats may be updated on crash)
        track:          the Track (needed for crash token color)
        roll_provider:  injectable roller

    Returns:
        AllAtOnceResult with per-die rolls, crash count, and how many
        moves the driver gets to make.
    """
    result = AllAtOnceResult()
    crash = 0
    moves = 0
    gear = ''
    for i, symbol in enumerate(seq):
        roll_result = roll_provider(symbol, dices)
        roll_log = {
            'step': i,
            'symbol': symbol,
            'result': roll_result,
        }
        result.rolls.append(roll_log)
        if symbol == 'B':
            moves -= 1
        if roll_result == '⚠️':
            crash += 1
        moves += 1
        if crash >= 3:
            if i > 0:
                gear = seq[i - 1]
            break
    if not gear and seq:
        gear = seq[-1]
    gear = coast_or_brake(driver, seq, gear)

    result.crash = crash
    result.moves = max(moves, 0)
    result.focus_tokens= len(seq)
    if crash >= 3:
        result.lost_control = True
        tile_color = track.tile(driver.tile_idx).color
        driver.stats.add_crash_tokens(gear, tile_color)
        try:
            gear_num = int(gear)
        except ValueError:
            gear_num = 0
        penalty_gear = '00' if gear_num >= 3 else '0'
        driver.current_gear = penalty_gear
        result.penalty_gear = penalty_gear
        result.final_gear = gear
    else:
        result.final_gear = gear
    return result

def apply_all_at_once_moves(
    aao_result: AllAtOnceResult,
    driver: Driver,
    track: Track,
    tile_idx: int,
    lane_idx: int,
    square_idx: int,
    final_gear: Optional[str] = None,
) -> None:
    """Apply the final position after an all-at-once turn.

    In this mode the player picks where they end up after seeing all
    rolls. This method sets the driver's position and gear.

    Args:
        aao_result:  the AllAtOnceResult from resolve_all_at_once()
        driver:      the Driver to update
        track:       the Track (for validation)
        tile_idx:    chosen final tile index
        lane_idx:    chosen final lane
        square_idx:  chosen final square
        final_gear:  override gear (if None, uses aao_result.final_gear)
    """
    driver.tile_idx = tile_idx
    driver.lane_idx = lane_idx
    driver.square_idx = square_idx

    if aao_result.lost_control:
        pass
    else:
        if final_gear is not None:
            driver.current_gear = final_gear
        else:
            driver.current_gear = aao_result.final_gear

    driver.stats.focus_tokens += aao_result.focus_tokens
