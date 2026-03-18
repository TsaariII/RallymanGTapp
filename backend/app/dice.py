from __future__ import annotations
import random
from typing import Dict, List, Callable, Optional, Tuple
from dataclasses import dataclass
from driver import Driver, do_movement
from track import Track, prompt_tile_index, prompt_lane_index, prompt_square_index

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
    for i, symbol in  enumerate(seq):
        if symbol == 'C' and i > 0:
            return seq[i - 1]
    if gear ==  'B':
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

@dataclass
class StepAction:
    """Describes what the driver does for a single movement step.
    
    choice: 1 = move forward same lane, 2 = change lane then move forward
    new_lane: required when choice == 2
    """
    choice: int = 1
    new_lane: Optional[int] = None

MoveDecider = Callable[[int, Driver, Track, str], StepAction]

def prompt_move_action(index: int, driver: Driver, track: Track, gear: str) -> StepAction:
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

RollProvider = Callable[[str, Dict[str, Dice]], str]
def random_roll(symbol: str, dices: Dict[str, Dice]) -> str:
    return dices[symbol].roll()

@dataclass
class DiceSequence:
    """Everything that happens during one dice sequence execution."""
    crash: int = 0
    final_gear: str = ''
    lost_control: bool = False
    steps: List[Dict] = None
    def __post_init__(self):
        if self.steps is None:
            self.steps = []

def resolve_turn(
    seq: List[str],
    dices: Dict[str, Dice],
    driver: Driver,
    track: Track,
    actions: MoveDecider = prompt_move_action,
    roll_provider: RollProvider = random_roll
) -> DiceSequence:
    result = DiceSequence()
    crash = 0
    gear = ''
    breaks: List[str] = []
    for index, symbol in enumerate(seq):
        log = {
            'step': index,
            'symbol': symbol,
            'result': None,
            'gear': None,
            'action': None,
            'crash_before': crash,
            'crash_after': None,
            'position_before': {
                'tile_idx': driver.tile_idx,
                'lane_idx': driver.lane_idx,
                'sqr_idx': driver.square_idx
            },
            'position_after': None
        }
        if symbol == 'B':
            breaks.append('B')
            continue
        for _ in breaks:
            b_res = roll_provider('B', dices)
            print(f" Brake roll: {b_res}")
            if b_res == '⚠️':
                crash += 1
        breaks.clear()
        roll_result = roll_provider(symbol, dices)
        log['result'] = roll_result
        print(f"  {symbol} -> {roll_result}")
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
            print(f"  *** LOST CONTROL on gear {final_gear} (crash={crash}) ***")
            tile_color = track.tile(driver.tile_idx).color
            driver.stats.add_crash_tokens(gear, tile_color)
            try:
                num = int(final_gear)
            except ValueError:
                num = 0
            penalty_gear = '00' if num >= 3 else '0'
            driver.current_gear = penalty_gear
            log['crash_after'] = crash
            log['position_after'] = {
                'tile_idx': driver.tile_idx,
                'lane_idx': driver.lane_idx,
                'sqr_idx': driver.square_idx
            }
            result.steps.append(log)
            return result
        action = actions(index, driver, track, resolved)
        log['action'] = {'choice': action.choice, 'new_lane': action.new_lane}
        crash = do_movement(track, driver, crash, resolved, action.choice, action.new_lane)
        log['crash_after'] = crash
        log['position_after'] = {
            'tile_idx': driver.tile_idx,
            'lane_idx': driver.lane_idx,
            'sqr_idx': driver.square_idx
        }
        if symbol != seq[-1]:
            choice = input(
                'Press Enter to continue or type exit to return to dice selection: '
            ).strip()
            if choice == 'exit':
                result.crash = crash
                result.final_gear = driver.current_gear
                return result

        result.steps.append(log)
        if seq and seq[-1] == 'C':
            gear = coast_or_brake(driver, seq, resolved)
        else:
            gear = symbol
        driver.current_gear = gear
    result.crash = crash
    result.final_gear = driver.current_gear
    return result

def roll_one_by_one(
    seq: List[str],
    dice: Dict,
    driver: Driver,
    track: Track
    ) -> None:
    result = resolve_turn(
        seq, dice, driver, track, 
        actions=prompt_move_action, 
        roll_provider=random_roll
    )
    if result.lost_control:
        lane = prompt_lane_index(track, driver.tile_idx)
        driver.lane_idx = lane
        square = prompt_square_index(track, driver.tile_idx, lane)
        driver.square_idx = square

    # crash = 0
    # gear = ''
    # breaks: List[str] = []
    # for symbol in seq:
    #     if symbol == 'B':
    #         breaks.append('B')
    #         continue
    #     for _ in breaks:
    #         b_res = dice['B'].roll()
    #         print(b_res)
    #         if b_res == '⚠️':
    #             crash += 1
    #     if symbol != 'B':
    #         breaks.clear()
    #     print(symbol, end=' ')
    #     result = dice[symbol].roll()
    #     if result == '⚠️':
    #         result = symbol
    #     if result in {'⬜️', '🟥'}:
    #        result = coast_or_brake(driver, seq, result)
    #     print(result)
    #     if result == '⚠️':
    #         crash += 1
    #     if crash == 3:
    #         final_gear = result
    #         if final_gear in {'C', 'B'}:
    #             final_gear = coast_or_brake(driver, seq, final_gear)
    #         print(f"You lost control on {final_gear} gear")
    #         tile_color = track.tile(driver.tile_idx).color
    #         driver.stats.add_crash_tokens(final_gear, tile_color)
    #         try:
    #             gear_num = int(final_gear)
    #         except ValueError:
    #             gear_num = 0
    #         penalty_gear = '00' if gear_num >= 3 else '0'
    #         driver.current_gear = penalty_gear
    #         lane = prompt_lane_index(track, driver.tile_idx)
    #         driver.lane_idx = lane
    #         square = prompt_square_index(track, driver.tile_idx, lane)
    #         driver.square_idx = square
    #         return
    #     # crash_before = crash
    #     change_lane_or_move(track, driver, crash, result)
    #     # if crash > crash_before:
    #     #     result = '⚠️'
    #     # else:
    #     #     result = ''
    #     if symbol != seq[-1]:
    #         choice = input(
    #             'Press Enter to continue or type exit to return to dice selection: '
    #         ).strip()
    #         if choice == 'exit':
    #             return
    #     if seq and seq[-1] == 'C':
    #         gear = coast_or_brake(driver, seq, result)
    #     else:
    #         gear = symbol
    #     driver.current_gear = gear

def roll_all_at_once(
    seq: List[str],
    dice: Dict[str, Dice],
    driver: Driver,
    track: Track
) -> None:
    tokens = len(dice)
    crash = 0
    moves = 0
    gear = ''
    for i, symbol in enumerate(seq):
        if crash == 3:
            if i > 0:
                gear = seq[i - 1]
            break
        print(symbol, end=' ')
        result = dice[symbol].roll()
        print(result)
        if symbol == 'B':
            moves -= 1
            tokens -= 1
        if result == '⚠️':
            crash += 1
        moves += 1
        if not gear and seq:
            gear = seq[-1]
        gear = coast_or_brake(driver, seq, gear)
    for i in range(moves):
        # print(f"Entering for dice {i + 1}")
        # prev_gear = seq[i]
        # if seq[i] in {'C', 'B'}:
        #     prev_gear = coast_or_brake(driver, seq, prev_gear)
        # change_lane_or_move(track, driver, crash, prev_gear)
        driver.stats.focus_tokens += 1
    if crash == 3:
        print(f"You lost control on {gear} gear")
        tile_color = track.tile(driver.tile_idx).color
        driver.stats.add_crash_tokens(gear, tile_color)
        try:
            gear_num = int(gear)
        except ValueError:
            gear_num = 0
        penalty_gear = '00' if gear_num >= 3 else '0'
        driver.current_gear = penalty_gear
        while True:
            try:
                tile_num = int(input(f"Enter tile number (1 - {track.length}): "))
            except ValueError:
                print("Invalid tile! Try again.")
                continue
            if 1 <= tile_num <= track.length:
                tile_num -= 1
                break
            print("Invalid tile! Try again.")
            driver.tile_idx = tile_num
        lane = prompt_lane_index(track, driver.tile_idx)
        driver.lane_idx = lane
        square = prompt_square_index(track, driver.tile_idx, lane)
        driver.square_idx = square
        print(f"{driver.name} is on gear {driver.current_gear}")
        print(f"Tokens earned: {tokens}")
        return
    tile_num = 0
    while True:
        try:
            tile_num = int(input(f"Enter tile number (1 - {track.length}): "))
        except ValueError:
            print("Invalid tile! Try again.")
            continue
        if 1 <= tile_num <= track.length:
            tile_num -= 1
            break
        print("Invalid tile! Try again.")
    # print(f"Tile number: {track.tiles[tile_num].number}")
    driver.tile_idx = tile_num
    lane = prompt_lane_index(track, driver.tile_idx)
    driver.lane_idx = lane
    square = prompt_square_index(track, driver.tile_idx, lane)
    driver.square_idx = square
    if moves < len(seq):
        last_idx = moves
    else:
        last_idx = len(seq) - 1
    if last_idx >= 0:
        driver.current_gear = seq[last_idx]
    if last_idx >= 0 and seq[last_idx] == 'C':
        driver.current_gear = coast_or_brake(driver, seq, gear)
        print(f"Gear: {gear}")
    print(f"{driver.name} is on gear {driver.current_gear}")
    print(f"Tokens earned: {tokens}")