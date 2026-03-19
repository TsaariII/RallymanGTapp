from __future__ import annotations
from enums import Tires, Weather
from stats import Stats
from tire import Tire
from track import Track

class Driver:
    def __init__(self, name: str, team: str, tires: Tires, weather: Weather) -> None:
        self.name = name
        self.team = team
        self.position: int = 0
        self.current_gear: str = '0'
        self.lap:int = 1
        self.stats: Stats = Stats()
        self.tile_idx: int = 0
        self.lane_idx: int = 0
        self.square_idx: int = 0
        self.inside_idx: int = 0
        self.starting_tile: int = 0
        self.tires: Tire = Tire(tires, weather)
    
    def move_forward(self, track: Track, crash: int, gear: str) -> int:
        """Move the driver one square forward along the current lane.
 
        Handles:
        - Exit warnings and max_gear_exit checks on the current square
        - Advancing to the next square or next tile
        - Merge placeholder resolution (M1 -> lane 1, M3 -> lane 3)
        - Enter warnings and max_gear_enter checks on the destination square
        - max_gear and max_gear_else_warning checks on the destination
 
        Returns the updated crash count.
        """
        tile = track.tile(self.tile_idx)
        current = tile.square_data(self.lane_idx, self.square_idx)
        lane_squares = tile.lane_squares.get(self.lane_idx)
        if not lane_squares:
            return crash
        def as_list(v):
            if v is None:
                return []
            return v if isinstance(v, list) else [v]
        warning_exit_lanes = as_list(current.get("exit_warning_lane"))
        max_gear_exit = current.get("max_gear_exit")
        max_gear_exit_lanes = as_list(current.get("max_gear_exit_lane"))
        if current.get("exit_warning") and self.lane_idx in warning_exit_lanes:
            crash += 1
        if current.get("max_gear_exit_lanes") and self.lane_idx in max_gear_exit_lanes:
            if max_gear_exit is not None and int(self.current_gear) > max_gear_exit:
                crash += 3
                if self.square_idx + 1 >= len(tile.lane_squares):
                    self.tile_idx += 1
                    self.square_idx = 0
                else:
                    self.square_idx += 1
                return crash
        if self.square_idx + 1 >= len(lane_squares):
            if self.tile_idx == 22:
                tile = track.tile(1)
                self.square_idx = 0
                next = tile.square_data(self.lane_idx, 1)
                if next.get("inside") is None and next.get("merge"):
                    merge_id = next.get("merge")
                    if merge_id == "M1":
                        self.lane_idx = 1
                        next = tile.square_data(self.lane_idx, self.square_idx)
                    if merge_id == "M3":
                        self.lane_idx = 3
                        next = tile.square_data(self.lane_idx, self.square_idx)
            else:
                tile = track.tile(self.tile_idx + 1)
                self.square_idx = 0
                self.tile_idx += 1
                next = tile.square_data(self.lane_idx, self.square_idx)
                print(
                    f"{self.name} moved to tile {self.tile_idx + 1}"
                    f"({track.tile(self.tile_idx + 1).color}) in lane {self.lane_idx}"
                )
                if next.get("inside") is None and next.get("merge"):
                    print("!!!! HERE 2 !!!!")
                    merge_id = next.get("merge")
                    if merge_id == "M1":
                        self.lane_idx = 1
                        next = tile.square_data(self.lane_idx, self.square_idx)
                    if merge_id == "M3":
                        self.lane_idx = 3
                        next = tile.square_data(self.lane_idx, self.square_idx)
        else:
            self.square_idx += 1
            next = tile.square_data(self.lane_idx, self.square_idx)
            if next.get("inside") is None and next.get("merge"):
                merge_id = next.get("merge")
                if merge_id == "M1":
                    self.lane_idx = 1
                    next = tile.square_data(self.lane_idx, self.square_idx)
                if merge_id == "M3":
                    self.lane_idx = 3
                    next = tile.square_data(self.lane_idx, self.square_idx)
        warning_enter_lanes = as_list(current.get("enter_warning_lane"))
        max_gear_enter = current.get("max_gear_enter")
        max_gear_enter_lanes = as_list(current.get("max_gear_enter_lane"))
        if next.get("enter_warning") and self.lane_idx in warning_enter_lanes:
            crash += 1
        if next.get("max_gear_enter_lanes") and self.lane_idx in max_gear_enter_lanes:
            if max_gear_enter is not None and int(self.current_gear) > max_gear_enter:
                crash += 3
                return crash
        max_gear = next.get("max_gear")
        if max_gear is not None and max_gear < int(gear):
            crash += 3
            return crash
        max_gear_else_warning = next.get("max_gear_else_warning")
        if max_gear_else_warning is not None and int(gear) > max_gear_else_warning:
            crash += 1
        return crash

    def apply_lane_change(self, track: Track, crash: int, new_lane: int) -> int:
        """Apply a lane change to new_lane."""
        tile = track.tile(self.tile_idx)
        prev_len = tile.lane_squares.get(self.lane_idx, [])
        new_len = tile.lane_squares.get(new_lane, [])
        if len(new_len) > len(prev_len):
            self.square_idx += 1
        if len(new_len) < len(prev_len) and self.square_idx != 0:
            self.square_idx -= 1
        self.lane_idx = new_lane
        return crash

def do_movement(
    track: Track,
    driver: Driver,
    crash: int,
    gear: str,
    choice: int,
    new_lane: int | None = None
    ) -> int:
        """Pure logic version of change_lane_or_move. No input() calls.
        Args:
            track:    the Track object
            driver:   the Driver to act on
            crash:    current crash counter
            gear:     the gear string for this move
            choice:   1 = move forward same lane, 2 = change lane then move
            new_lane: required if choice == 2; the lane index to switch to
    
        Returns:
            Updated crash count after the action.
        """
        if choice == 1:
            crash = driver.move_forward(track, crash, gear)
        elif choice == 2:
            if new_lane is None:
                raise ValueError('new_lane is required when choice == 2')
            crash = driver.apply_lane_change(track, crash, new_lane)
            crash = driver.move_forward(track, crash, gear)
        else:
            raise ValueError(f"Invalid choice: {choice}. Must be 1 or 2.")
        return crash