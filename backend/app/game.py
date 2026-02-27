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
            if t in {'C', 'B', '00'}:
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
    
    def _gear_value_int(self, gear: str) -> int:
        """Convert a gear string to an int for sorting.

        Rallyman GT sometimes uses '00' to represent a crash penalty gear.
        We treat that as lower than 0.
        """
        if gear == '00':
            return -1
        try:
            return int(gear)
        except Exception:
            return -1

    def _indside_lane_value(self, driver: Driver) -> int:
        """Lower is more inside. Falls back to 100 if unknown."""
        if not (0 <= driver.tile_idx < self.track.length):
            return 100
        tile = self.track.tile(driver.tile_idx)
        squares = tile.lane_squares.get(driver.lane_idx)
        if not squares or not (0 <= driver.square_idx < len(squares)):
            return 100
        inside = tile.square_data(driver.lane_idx, driver.square_idx).get("inside")
        if inside is None:
            return 100
        try:
            return int(inside)
        except Exception:
            return 100

    def check_positions(self, drivers: List[Driver]) -> None:
        """Update each driver's race position (1 = leader).

        Race order rules (leaderboard):
        - who is on the latest lap
        - who is further on the track (tile, then square)
        - who has higher gear
        - who has inside lane if on the same square, but different lanes
        """
        def key_func(d: Driver) -> Tuple[int, int, int , int, int]:
            lap = d.lap
            tile_idx = d.tile_idx
            square_idx = d.square_idx
            gear = self._gear_value_int(d.current_gear)
            inside = self._indside_lane_value(d)
            return (-lap, -tile_idx, -square_idx, -gear, inside)
        ordered = sorted(drivers, key=key_func)
        for pos, d in enumerate(ordered, start=1):
            d.position = pos
        drivers [:] = ordered
    
    def sort_drivers_for_round(self, drivers: List[Driver]) -> None:
        """Sort drivers in-place for the next round turn order.

        Turn order rules:
        - who has highest gear
        - who is on the latest lap
        - who is further on the track (tile, then square)
        - who has inside lane if on the same square, but different lanes
        """
        def key_func(d: Driver) -> tuple[int, int, int, int, int]:
            gear = self._gear_value_int(d.current_gear)
            lap = d.lap
            tile = d.tile_idx
            square = d.square_idx
            inside = self._indside_lane_value(d)
            return (-gear, -lap, -tile, -square, inside)
        drivers.sort(key=key_func)

    def _is_square_free(
        self,
        tile_idx: int,
        lane_idx: int,
        square_idx: int,
        ignore_driver=None,
    ) -> bool:
        """True if no other driver occupies (tile_idx, lane_idx, square_idx)."""
        for d in self.drivers:  # adjust if your list is named differently
            if ignore_driver is not None and d is ignore_driver:
                continue
            if (d.tile_idx, d.lane_idx, d.square_idx) == (tile_idx, lane_idx, square_idx):
                return False
        return True

    def set_driver_starting_position(
        self,
        driver: Driver,
        positions: Set[int]
    ) -> None:
        """Set grid and on-track starting tile/lane/square for one driver."""
        # self.track.print_track()
        driver.position = self.prompt_starting_grid_position(driver, positions)
        while True:
            tile_idx = prompt_tile_index(self.track)
            if tile_idx != 0:
                driver.lap = 0
            lane_idx = prompt_lane_index(self.track, tile_idx)
            square_idx = prompt_square_index(self.track, tile_idx, lane_idx)
            if not self._is_square_free(tile_idx, lane_idx, square_idx, ignore_driver=driver):
                print("Square already occupied! Pick another.")
                continue
            break
        driver.starting_tile = tile_idx
        driver.tile_idx = tile_idx
        driver.lane_idx = lane_idx
        driver.square_idx = square_idx
    
    def race_round(
        self,
        drivers: List[Driver],
        dices: Dict[str, Dice]
    ) -> None:
        """Run one full round where each driver takes a turn."""
        self.check_positions(drivers)
        self.sort_drivers_for_round(drivers)
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
                raw = input('Enter dice for this driver (comma separated): ')
                if raw == '':
                    print("Empty input; Try again.")
                    continue
                seq = self.parse_input(raw)
                if not seq:
                    print("Invalid dice input. Please try again.")
                    continue
                try:
                    if seq[0] == '00':
                        driver.current_gear = '0'
                        print(f"{driver.name} changed to gear 0. End of turn")
                        break
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