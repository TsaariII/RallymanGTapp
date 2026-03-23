from __future__ import annotations
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from backend.app.models.enums import Weather, Tires
from backend.app.models.track import Track
from backend.app.models.team import Team
from backend.app.models.driver import Driver
from backend.app.models.dice import Dice, create_dice, all_at_once, resolve_turn, AllAtOnceResult
from backend.app.models.tire import Tire
from backend.app.models.dice import (
    Dice,
    DiceSequence,
    StepAction,
    MoveDecider,
    RollProvider,
    create_dice,
    random_roll,
    resolve_turn
)

@dataclass
class TurnInput:
    """Everything needed to execute one driver's turn."""
    name: str
    dices: List[str]
    actions: List[StepAction]

@dataclass
class TurnResult:
    """What happened during one driver's turn."""
    name: str
    results: DiceSequence
    pos_after: Dict
    gear_after: str
    lost_control: bool

@dataclass
class RoundResult:
    """Results of a full race round (all drivers)."""
    turn_results: List[TurnResult] = field(default_factory=list)
    standings: List[Dict] = field(default_factory=list)



class Game:
    def __init__(self, track_name: str) -> None:
        self.track = Track(track_name)
        self.weather: Weather = Weather.DRY
        self.teams: List[Team] = []
        self.drivers: List[Driver] = []
        self.dices: Dict[str, Dice] = {
            face: create_dice(face)
            for face in ('1', '2', '3', '4', '5', '6', 'C', 'B')
        }
        self._pending_aao: Dict[str, AllAtOnceResult] = {}
    
    def set_weather(self, weather: Weather) -> None:
        """Set the race weather. Call before adding teams/drivers."""
        self.weather = weather
    
    def add_team(
        self,
        team_name: str,
        d1_name: str,
        d2_name: str,
        tires: Tires = Tires.NORMAL
    ) -> Team:
        """Create a team with two drivers and add them to the game.
        Returns the created Team so callers can inspect it if needed.
        """
        team = Team(team_name, d1_name, d2_name, tires, self.weather)
        self.teams.append(team)
        self.drivers.extend(team.drivers)
        return team
    
    def set_tires(self, name: str, type: Tires) -> None:
        """Set tire type for a specific driver by name.
        Raises ValueError if the driver is not found.
        """
        driver = self._find_driver(name)
        driver.tires = Tire(type, self.weather)

    def set_starting_positions(
        self,
        name: str,
        position: int,
        tile_idx: int,
        lane_idx: int,
        square_idx: int
    ) -> None:
        """Set a driver's starting grid position and on-track location.
        Validates:
        - grid_position is 1–12 and not already taken
        - tile/lane/square exist and the square is not occupied
        Raises ValueError on any validation failure.
        """
        driver = self._find_driver(name)
        if not (1 <= position <= 12):
            raise ValueError(f"Grid position must be 1–12, got {position}")
        taken = {d.position for d in self.drivers if d is not driver and d.position > 0}
        if position in taken:
            raise ValueError(f"Grid position {position} is already taken")
        if not (0 <= tile_idx < self.track.length):
            raise ValueError(
                f"Tile index must be 0–{self.track.length - 1}, got {tile_idx}"
            )
        tile = self.track.tile(tile_idx)
        if lane_idx not in tile.lane_squares or not tile.lane_squares[lane_idx]:
            raise ValueError(
                f"Lane {lane_idx} does not exist or is empty on tile {tile.number}"
            )
        lane_len = len(tile.lane_squares[lane_idx])
        if not (0 <= square_idx < lane_len):
            raise ValueError(
                f"Square index must be 0–{lane_len - 1} for tile {tile.number} "
                f"lane {lane_idx}, got {square_idx}"
            )
        if not self._is_square_free(tile_idx, lane_idx, square_idx, ignore_driver=driver):
            raise ValueError(
                f"Square (tile={tile.number}, lane={lane_idx}, square={square_idx}) "
                f"is already occupied"
            )
        driver.position = position
        driver.starting_tile = tile_idx
        driver.tile_idx = tile_idx
        driver.lane_idx = lane_idx
        driver.square_idx = square_idx
        if tile_idx != 0:
            driver.lap = 0
    
    def driver_turn(
        self,
        name: str,
        dices: List[str],
        actions: List[StepAction],
        roll_provider: RollProvider = random_roll
    ) -> TurnResult:
        """Execute a single driver's turn.
 
        Args:
            name:    which driver is rolling
            dices:  list of dice symbols, e.g. ['3', '4', 'C']
            actions:        one StepAction per die — what to do after each roll
            roll_provider:  how dice are rolled (random by default, injectable for tests)
 
        Returns:
            TurnResult with the full DiceSequence outcome and driver state after.
        """
        driver = self._find_driver(name)
        if dices and dices[0] == '00':
            driver.current_gear = '0'
            return TurnResult(
                name=name,
                results=DiceSequence(crash=0, final_gear='0', lost_control=False),
                pos_after=self._driver_location_dict(driver),
                gear_after='0',
                lost_control=False
            )
        action_list = list(actions)
        def action_provider(index:int, d: Driver, t: Track, gear: str) -> StepAction:
            if index < len(action_list):
                return action_list[index]
            return StepAction(choice=1)
        dice_result = resolve_turn(
            seq=dices,
            dices=self.dices,
            driver=driver,
            track=self.track,
            actions=action_provider,
            roll_provider=roll_provider
        )
        driver.stats.turns += 1
        driver.stats.add_lap_time(driver.current_gear)
        return TurnResult(
            name=name,
            results=dice_result,
            pos_after=self._driver_location_dict(driver),
            gear_after=driver.current_gear,
            lost_control=dice_result.lost_control
        )
    
    def execute_round(
        self,
        inputs: List[TurnInput],
        roll_provider: RollProvider = random_roll
    ) -> RoundResult:
        """Execute a full race round.
 
        Updates positions and turn order, then runs each driver's turn
        in the order determined by sort_drivers_for_round().
 
        Args:
            turn_inputs: one TurnInput per driver, keyed by driver_name.
                         The order in the list doesn't matter — drivers are
                         sorted internally.
            roll_provider: injectable dice roller.
 
        Returns:
            RoundResult with per-driver outcomes and final standings.
        """
        self.check_positions(self.drivers)
        self.sort_drivers_for_round(self.drivers)
        input_by_name = {ti.name: ti for ti in inputs}
        round_result = RoundResult()
        for driver in self.drivers:
            ti = input_by_name.get(driver.name)
            if ti is None:
                continue
            turn_result = self.driver_turn(
                name=ti.name,
                dices=ti.dices,
                actions=ti.actions,
                roll_provider=roll_provider
            )
            round_result.turn_results.append(turn_result)
        self.check_positions(self.drivers)
        round_result.standings = self.get_standings()
        return round_result
    
    def get_standings(self) -> List[Dict]:
         """Return current race standings as a list of dicts."""
         self.check_positions(self.drivers)
         return [
            {
                'position': d.position,
                'name': d.name,
                'team': d.team,
                'gear': d.current_gear,
                'lap': d.lap,
                'tile': d.tile_idx,
                'lane': d.lane_idx,
                'square': d.square_idx,
                'total_time': d.stats.total_time_str
            }
            for d in self.drivers
         ]

    def get_driver_state(self, name: str) -> Dict:
        """Return full state of a single driver."""
        d = self._find_driver(name)
        return {
            'name': d.name,
            'team': d.team,
            'position': d.position,
            'gear': d.current_gear,
            'lap': d.lap,
            'tile': d.tile_idx,
            'lane': d.lane_idx,
            'square': d.square_idx,
            'starting_tile': d.starting_tile,
            'tires': {
                'type': d.tires.type_label,
                'condition': d.tires.condition.value,
                'turns': d.tires.turns
            },
            'stats': {
                'turns': d.stats.turns,
                'total_time': d.stats.total_time_str,
                'lap_times': d.stats.lap_time_str,
                'focus_tokens': d.stats.focus_tokens,
                'lost_gear': d.stats.lost_gear,
                'lost_brake': d.stats.lost_brake,
                'lost_coast': d.stats.lost_coast,
                'weather_token': d.stats.weather_token,
                'yellow_flag': d.stats.yellow_flag,
                'green_flag': d.stats.green_flag
            }
        }

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
        for d in self.drivers:
            if ignore_driver is not None and d is ignore_driver:
                continue
            if (d.tile_idx, d.lane_idx, d.square_idx) == (tile_idx, lane_idx, square_idx):
                return False
        return True

    def _find_driver(self, name: str) -> Driver:
        """Look up a driver by name. Raises ValueError if not found."""
        for d in self.drivers:
            if d.name == name:
                return d
        raise ValueError("Driver '{name}' not found in game")
    
    def _driver_location_dict(self, driver: Driver) -> Dict:
        return {
            'tile_idx': driver.tile_idx,
            'lane_idx': driver.lane_idx,
            'square_idx': driver.square_idx
        }
