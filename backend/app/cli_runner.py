from __future__ import annotations
import time
from typing import Dict, List, Set
from backend.app.models.enums import Weather, Tires
from backend.app.models.game import Game, TurnInput
from backend.app.models.track import (
    Track,
    prompt_tile_index,
    prompt_lane_index,
    prompt_square_index
)
from backend.app.models.dice import (
    Dice,
    StepAction,
    DiceSequence,
    AllAtOnceResult,
    create_dice,
    random_roll,
    prompt_move_action,
    prompt_continue,
    resolve_turn,
    all_at_once,
    apply_all_at_once_moves
)
from models.driver import Driver

def cli_roll(symbol: str, dices: Dict[str, Dice]) -> str:
    result = random_roll(symbol, dices)
    print(f"  {symbol} -> {result}")
    return result

def prompt_weather() -> Weather:
    """Ask the user for race weather."""
    while True:
        choice = input('Select weather (Dry/Wet): ').strip().lower()
        if choice in ('dry', 'd'):
            return Weather.DRY
        if choice in ('wet', 'w'):
            return Weather.WET
        print("Invalid choice. Please type 'Dry' or 'Wet'.")

def prompt_tire_type(driver: Driver) -> Tires:
    """Ask the user to pick a tire type for one driver."""
    while True:
        try:
            choice = int(
                input(
                    f"Select tire type for {driver.name} "
                    f"from team {driver.team}: "
                )
            )
        except ValueError:
            print('Invalid choice. Please enter 1, 2 or 3.')
            continue
        return {1: Tires.NORMAL, 2: Tires.SPRINT, 3: Tires.WET}[choice]

def prompt_strating_position(driver: Driver, taken: Set[int]) -> int:
    """Ask for a unique grid position 1–12."""
    while True:
        try:
            pos = int(
                input(
                    f"Enter position for {driver.name} from team "
                    f"{driver.team} (1-12): "
                )
            )
        except ValueError:
            print('Invalid or duplicate position! Try again.')
            continue
        if not (1 <= pos <= 12) or pos in taken:
            print('Invalid or duplicate position! Try again.')
            continue
        taken.add(pos)
        return pos

def prompt_dice_seq(game: Game) -> List[str]:
    """Ask the user for a comma-separated dice sequence."""
    while True:
        raw = input('Enter dice for this driver (comma separated): ')
        if raw == '':
            print('Empty input; Try again.')
            continue
        seq = game.parse_input(raw)
        if not seq:
            print('Invalid dice input. Please try again.')
            continue
        return seq

def print_countdown() -> None:
    """Start lights animation."""
    for  i in range(1, 6):
        print('\r' + '🔴 ' * i, end='', flush=True)
        time.sleep(1)
    print('\nRace begins!!')

def setup_teams(game: Game) -> None:
     """Create the default teams."""
     game.add_team('Evante', 'Collins', 'Cooper')

def setup_tires(game: Game) -> None:
    """Prompt tire selection for every driver."""
    print('\n=== Tire Selection ===')
    print('Available tire types:')
    print('1. Normal\n2. Sprint\n3. Wet\n')
    for driver in game.drivers:
        type = prompt_tire_type(driver)
        game.set_tires(driver.name, type)

def setup_positions(game: Game) -> None:
    """Prompt starting grid and on-track positions for each driver."""
    grid_taken: Set[int] = set()
    for driver in game.drivers:
        print(
            f"Setting position for {driver.name} "
            f"(gear: {driver.current_gear}) "
            f"from team {driver.team}"
        )
        pos = prompt_strating_position(driver, grid_taken)
        while True:
            tile_idx = prompt_tile_index(game.track)
            lane_idx = prompt_lane_index(game.track, tile_idx)
            square_idx = prompt_square_index(game.track, tile_idx, lane_idx)
            try:
                game.set_starting_positions(
                    driver.name, pos, tile_idx, lane_idx, square_idx
                )
                break
            except ValueError as e:
                print(f"{e} Try again.")

def print_step(step: Dict) -> None:
    """Print one step from a DiceSequence log."""
    print(f"  {step['symbol']} -> {step['result']}")
    if step.get('brake_rolls'):
        for b in step['brake_rolls']:
            print(f"B -> {b}")
    if step['crash_after'] is not None and step['crash_after'] > step['crash_before']:
        added = step['crash_after'] - step['crash_before']
        print(f"    +{added} crash (total: {step['crash_after']})")
    if step['pos_after'] and step['pos_after'] != step['pos_before']:
        print(
            f"    Moved: tile {step['pos_before']['tile_idx']+1} L{step['pos_before']['lane_idx']} "
            f"S{step['pos_before']['sqr_idx']} -> "
            f"tile {step['pos_after']['tile_idx']+1} L{step['pos_after']['lane_idx']} "
            f"S{step['pos_after']['sqr_idx']}"
        )

def turn_one_by_one(game: Game, driver: Driver) -> None:
    """Execute a one-by-one turn using resolve_turn with CLI prompts."""
    seq = prompt_dice_seq(game)
    if seq[0] == '00':
        driver.current_gear = '0'
        print(f"{driver.name} changed to gear 0. End of turn")
        return
    dice_result = resolve_turn(
        seq=seq,
        dices=game.dices,
        driver=driver,
        track=game.track,
        actions=prompt_move_action,
        roll_provider=cli_roll,
        continue_decider=prompt_continue
    )
    for step in dice_result.steps:
        print_step(step)
    if dice_result.lost_control:
        print(f"  *** LOST CONTROL (crash={dice_result.crash}) ***")
        print(f"  Penalty gear: {driver.current_gear}")
        lane = prompt_lane_index(game.track, driver.tile_idx)
        driver.lane_idx = lane
        square = prompt_square_index(game.track, driver.tile_idx, lane)
        driver.square_idx = square
    elif dice_result.stopped_early:
        print(f"  Sequence stopped early. Gear: {driver.current_gear}")
    driver.stats.turns += 1
    driver.stats.add_lap_time(driver.current_gear)

def turn_all_at_once(game: Game, driver: Driver) -> None:
    """Execute an all-at-once turn: roll everything, then position manually."""
    seq = prompt_dice_seq(game)
    if seq[0] == '00':
        driver.current_gear = '0'
        print(f"{driver.name} changed to gear 0. End of turn")
        return
    aao = all_at_once(
        seq=seq,
        dices=game.dices,
        driver=driver,
        track=game.track,
        roll_provider=random_roll
    )
    for roll in aao.rolls:
        print(f"  {roll['symbol']} -> {roll['result']}")
    if aao.lost_control:
        print(f"  *** LOST CONTROL on gear {aao.final_gear} (crash={aao.crash}) ***")
        print(f"  Penalty gear: {aao.penalty_gear}")
    print(f"  Moves available: {aao.moves}")
    print(f"  Focus tokens earned: {aao.focus_tokens}")
    while True:
        try:
            tile = int(input(f"Enter tile number (1 - {game.track.length}): "))
        except ValueError:
            print("Invalid tile! Try again.")
            continue
        if 1 <= tile <= game.track.length:
            tile = tile - 1
            break
        print("Invalid tile! Try again.")
    lane = prompt_lane_index(game.track, tile)
    square = prompt_square_index(game.track, tile, lane)
    apply_all_at_once_moves(
        aao_result=aao,
        driver=driver,
        track=game.track,
        tile_idx=tile,
        lane_idx=lane,
        square_idx=square
    )
    print(f"  {driver.name} is on gear {driver.current_gear}")
    driver.stats.turns += 1
    driver.stats.add_lap_time(driver.current_gear)

def run_round(game: Game) -> None:
     """Run one full round: prompt dice and actions for each driver, execute turns."""
     game.check_positions(game.drivers)
     game.sort_drivers_for_round(game.drivers)
     for driver in game.drivers:
        print(
            f"\nNow rolling for {driver.name} "
            f"(Gear {driver.current_gear}) "
            f"from team {driver.team} "
            f"(Position {driver.position})"
        )
        print('\tSTATS')
        driver.stats.print_stats()
        while True:
            try:
                mode = int(
                    input('Choose roll mode: (1) one by one, (2) all at once: ')
                )
            except ValueError:
                print('Invalid roll mode. Try again.')
                continue
            if mode in (1, 2):
                break
            print('Invalid roll mode. Try again.')
        if mode == 1:
            turn_one_by_one(game, driver)
        else:
            turn_all_at_once(game, driver)


def race_loop(game: Game) -> None:
    """Loop race rounds until user stops."""
    while True:
        run_round(game)
        cont = input('End of race turn. Continue to next? (y/n): ').strip().lower()
        if cont.startswith('n'):
            break
        
def main() -> None:
    track_name = input('Enter track name: ').strip()
    if not track_name:
        print('No track name provided. Exiting.')
        return
    game = Game(track_name)
    game.set_weather(prompt_weather())
    setup_teams(game)
    setup_tires(game)
    setup_positions(game)
    print_countdown()
    race_loop(game)

if __name__ == '__main__':
    main()
