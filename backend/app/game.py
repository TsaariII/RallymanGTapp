from __future__ import annotations
import time
from typing import Dict, List, Set, Tuple
from enums import Weather, Tires
from track import (
    Track,
    prompt_tile_index,
    prompt_lane_index,
    prompt_square_index
)
from team import Team
from driver import Driver
from dice import Dice, create_dice, roll_all_at_once, roll_one_by_one
from tire import Tire

class Game:
    def __init__(self, track_name: str) -> None:
        self.track = Track(track_name)
        self.weather: Weather = Weather.DRY
        self.teams: List[Team] = []
        self.drivers: List[Driver] = []
        self.set_weather()
    
    def set_weather(self) -> None:
        """Ask the user for race weather."""
        while True:
            choice = input('Select weather (Dry/Wet): ').strip().lower()
            if choice in ('dry', 'd'):
                self.weather = Weather.DRY
                break
            if choice in ('wet', 'w'):
                self.weather = Weather.WET
                break
            print("Invalid choice. Please type 'Dry' or 'Wet'.")

    def setup_game(self) -> None:
        """Create teams and drivers."""
        self.teams = [
            Team("Evante", "Collins", "Cooper", Tires.NORMAL, self.weather)
        ]
        self.drivers = [driver for team in self.teams for driver in team.drivers]

    def set_tires(self) -> None:
        """Let user choose tire type per driver."""
        print("\n=== Tire Selection ===")
        print("Available tire types:")
        print("1. Normal\n2. Sprint\n3. Wet\n")
        for team in self.teams:
            for driver in team.drivers:
                while True:
                    try:
                        choice = int(
                            input(
                                f"Select tire type for {driver.name} "
                                f"from team {driver.team}: "
                            )
                        )
                    except ValueError:
                        print('Invald choice. Please enter 1, 2 or 3.')
                        continue
                    if choice not in (1, 2, 3):
                        print('Invald choice. Please enter 1, 2 or 3.')
                        continue
                    break
                tire_type = {
                    1: Tires.NORMAL,
                    2: Tires.SPRINT,
                    3: Tires.WET
                }[choice]
                driver.tires = Tire(tire_type, self.weather)
    
    def set_driver_positions(self) -> None:
        """Prompt starting grid and on-track positions for each driver."""
        grid_pos: Set[int] = set()
        for driver in self.drivers:
            print(
                f"Setting position for {driver.name} "
                f"(gear: {driver.current_gear}) "
                f"from team {driver.team}"
            )
            self.set_driver_starting_position(driver, grid_pos)
    
    def print_countdown(self) -> None:
        """Start lights animation."""
        for  i in range(1, 6):
            print('\r' + '🔴 ' * i, end='', flush=True)
            time.sleep(1)
        print('\nRace begins!!')
    
    def parse_input(self, raw: str) -> List[str]:
        """
        Parse dice input like: '1,2,3,C,B'
        Returns list of tokens or [] if invalid.
        """
        seq: List[str] = []
        for token in raw.split(','):
            t = token.strip().upper()
            if not t:
                continue
            if t in {'C', 'B'}:
                seq.append(t)
            else:
                if not t.isdigit():
                    return []
                value = int(t)
                if 1 <= value <= 6:
                    seq.append(t)
                else:
                   return []
        return seq

    def prompt_starting_grid_position(
        self,
        driver: Driver,
        positions: Set[int]
    ) -> int:
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
                print("Invalid or duplicate position! Try again.")
                continue
            if not (1 <= pos <= 12) or pos in positions:
                print("Invalid or duplicate position! Try again.")
                continue
            positions.add(pos)
            return pos
    
    def check_positions(self, drivers: List[Driver]) -> None:
        """
        Sort drivers by track position:
        - higher lap
        - further tile_index
        - further square_index
        - more inside lane (lower inside_priority)
        """
        def key_func(d: Driver) -> Tuple[int, int, int , int]:
            lap = d.lap
            tile_idx = d.tile_idx
            square_idx = d.square_idx
            inside = 100
            if 0 <= tile_idx < self.track.length:
                tile = self.track.tile(tile_idx)
                inside = tile.inside_priority_for_lane(d.lane_idx)
            return (-lap, -tile_idx, -square_idx, inside)
        drivers. sort(key=key_func)
    
    def set_driver_starting_position(
        self,
        driver: Driver,
        positions: Set[int]
    ) -> None:
        """Set grid and on-track starting tile/lane/square for one driver."""
        # self.track.print_track()
        driver.position = self.prompt_starting_grid_position(driver, positions)
        tile_idx = prompt_tile_index(self.track)
        driver.starting_tile = tile_idx
        driver.tile_idx = tile_idx
        if tile_idx != 0:
            driver.lap = 0
        lane_idx = prompt_lane_index(self.track, tile_idx)
        driver.lane_idx = lane_idx
        square_idx = prompt_square_index(self.track, tile_idx, lane_idx)
        driver.square_idx = square_idx
    
    def race_round(
        self,
        drivers: List[Driver],
        dices: Dict[str, Dice]
    ) -> None:
        """Run one full round where each driver takes a turn."""
        self.check_positions(drivers)
        drivers.sort(key=lambda d: d.position)
        for driver in drivers:
            print(
                f"Now rolling for {driver.name} "
                f"(Gear {driver.current_gear}) "
                f"from team {driver.team} "
                f"(Position {driver.position})"
            )
            print("\tSTATS")
            driver.stats.print_stats()
            while True:
                raw = input("Enter dice for this driver (comma separated): ")
                if raw == '':
                    print("Empty input; aborting this driver's turn.")
                    return
                seq = self.parse_input(raw)
                if not seq:
                    print("Invalid dice input. Please try again.")
                    continue
                try:
                    mode = int(
                        input("Choose roll mode: (1) one by one, (2) all at once: ")
                    )
                except ValueError:
                    print('Invalid roll mode. Try again.')
                    continue
                if mode == 1:
                    roll_one_by_one(seq, dices, driver, self.track)
                elif mode == 2:
                    roll_all_at_once(seq, dices, driver, self.track)
                else:
                    print("Invalid roll mode.")
                    continue
                driver.stats.turns += 1
                driver.stats.add_lap_time(driver.current_gear)
                break
    
    def race_loop(self) -> None:
        """Loop race rounds until user stops."""
        dices: Dict[str, Dice] = {
            face: create_dice(face)
            for face in ("1", "2", "3", "4", "5", "6", "C", "B")
        }
        while True:
            self.race_round(list(self.drivers), dices)
            cont = input('End of race turn. Continue to next? (y/n): ').strip().lower()
            if cont.startswith('n'):
                break

    def start(self) -> None:
        """Run full game setup and start the race."""
        self.setup_game()
        self.set_tires()
        self.set_driver_positions()
        self.print_countdown()
        self.race_loop()