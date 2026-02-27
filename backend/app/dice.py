from __future__ import annotations
import random
from typing import Dict, List
from driver import Driver, change_lane_or_move
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

def roll_one_by_one(
    seq: List[str],
    dice: Dict,
    driver: Driver,
    track: Track
    ) -> None:
    crash = 0
    gear = ''
    breaks: List[str] = []
    for symbol in seq:
        if symbol == 'B':
            breaks.append('B')
            continue
        for _ in breaks:
            b_res = dice['B'].roll()
            print(b_res)
            if b_res == '⚠️':
                crash += 1
        if symbol != 'B':
            breaks.clear()
        print(symbol, end=' ')
        result = dice[symbol].roll()
        if result == '⚠️':
            result = symbol
        if result in {'⬜️', '🟥'}:
           result = coast_or_brake(driver, seq, result)
        print(result)
        if result == '⚠️':
            crash += 1
        if crash == 3:
            final_gear = result
            if final_gear in {'C', 'B'}:
                final_gear = coast_or_brake(driver, seq, final_gear)
            print(f"You lost control on {final_gear} gear")
            tile_color = track.tile(driver.tile_idx).color
            driver.stats.add_crash_tokens(final_gear, tile_color)
            try:
                gear_num = int(final_gear)
            except ValueError:
                gear_num = 0
            penalty_gear = '00' if gear_num >= 3 else '0'
            driver.current_gear = penalty_gear
            lane = prompt_lane_index(track, driver.tile_idx)
            driver.lane_idx = lane
            square = prompt_square_index(track, driver.tile_idx, lane)
            driver.square_idx = square
            return
        change_lane_or_move(track, driver, crash, result)
        if symbol != seq[-1]:
            choice = input(
                'Press Enter to continue or type exit to return to dice selection: '
            ).strip()
            if choice == 'exit':
                return
        if seq and seq[-1] == 'C':
            gear = coast_or_brake(driver, seq, result)
        else:
            gear = symbol
        driver.current_gear = gear

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