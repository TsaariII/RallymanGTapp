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
        """Move the driver one square forward along the current lane."""
        tile = track.tile(self.tile_idx)
        current = tile.square_data(self.lane_idx, self.square_idx)
        print(f"*BEGIN* Position on track:\n\tTile: {track.tile(self.tile_idx).number}\n\tLane: {self.lane_idx}\n\tSquare: {self.square_idx}")
        lane_squares = tile.lane_squares.get(self.lane_idx)
        if not lane_squares:
            print("Error: driver is in a non-existing or empty lane!")
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
                    print(
                            f"{self.name} moved to tile {self.tile_idx + 1}"
                            f"({track.tile(self.tile_idx + 1).color}) in lane {self.lane_idx}"
                        )
                else:
                    self.square_idx += 1
                    print(f"{self.name} moved forward one square")
                return crash
        # print(f"Square: {self.square_idx}")
        # print(f"Lane len: {len(lane_squares)}")
        if self.square_idx + 1 >= len(lane_squares):
            if self.tile_idx == 22:
                tile = track.tile(1)
                self.square_idx = 0
                next = tile.square_data(self.lane_idx, 1)
                print(
                    f"{self.name} moved to tile {self.tile_idx + 1}"
                    f"({track.tile(self.tile_idx + 1).color}) in lane {self.lane_idx}"
                )
                if next.get("inside") is None and next.get("merge"):
                    print("!!!! HERE 1 !!!!")
                    merge_id = next.get("merge")
                    if merge_id == "M1":
                        self.lane_idx = 1
                        next = tile.square_data(self.lane_idx, self.square_idx)
                        # print(f"Tile index: {self.tile_idx}")
                        # print(f"Lane index: {self.lane_idx}")
                        # print(f"Square index: {self.square_idx}")
                    if merge_id == "M3":
                        self.lane_idx = 3
                        next = tile.square_data(self.lane_idx, self.square_idx)
            else:
                tile = track.tile(self.tile_idx + 1)
                self.square_idx = 0
                self.tile_idx += 1
                # print(f"Tile index: {self.tile_idx}")
                # print(f"Lane index: {self.lane_idx}")
                # print(f"Square index: {self.square_idx}")
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
                        # print(f"Tile index: {self.tile_idx}")
                        # print(f"Lane index: {self.lane_idx}")
                        # print(f"Square index: {self.square_idx}")
                    if merge_id == "M3":
                        self.lane_idx = 3
                        next = tile.square_data(self.lane_idx, self.square_idx)
        else:
            self.square_idx += 1
            print(f"{self.name} moved forward one square")
            next = tile.square_data(self.lane_idx, self.square_idx)
            # print(f"Next tile: {next}")
            if next.get("inside") is None and next.get("merge"):
                print("!!!! HERE 3 !!!!")
                merge_id = next.get("merge")
                if merge_id == "M1":
                    self.lane_idx = 1
                    next = tile.square_data(self.lane_idx, self.square_idx)
                    # print(f"Tile index: {self.tile_idx}")
                    # print(f"Lane index: {self.lane_idx}")
                    # print(f"Square index: {self.square_idx}")
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
        print(f"*END* Position on track:\n\tTile: {track.tile(self.tile_idx).number}\n\tLane: {self.lane_idx}\n\tSquare: {self.square_idx}")
        return crash

    def apply_lane_change(self, track: Track, crash: int, new_lane: int) -> int:
        """Apply a lane change to new_lane."""
        tile = track.tile(self.tile_idx)
        prev_len = tile.lane_squares.get(self.lane_idx, [])
        new_len = tile.lane_squares.get(new_lane, [])
        if len(new_len) > len(prev_len):
            print(f"1 Lane lengths\n\tPrev: {len(prev_len)}\n\tNew: {len(new_len)}")
            self.square_idx += 1
        if len(new_len) < len(prev_len) and self.square_idx != 0:
            print(f"2 Lane lengths\n\tPrev: {len(prev_len)}\n\tNew: {len(new_len)}")
            self.square_idx -= 1
        self.lane_idx = new_lane
        print(f"{self.name} switched to lane {self.lane_idx}")
        return crash

    # def change_lane(self, track: Track, crash: int) -> None:
    #     """Change lane left or right on the current tile."""
    #     tile = track.tile(self.tile_idx)
    #     while True:
    #         try:
    #             lane = int(
    #                 input('Enter lane change number (1, 2, 3): ')
    #             )
    #         except ValueError:
    #             print('Invalid lane change input! Try again.')
    #             continue
    #         # print(f"new lane: {lane}")
    #         if 1 <= lane <= tile.lanes:
    #             self.apply_lane_change(track, crash, lane)
    #             break
    #         print("Invalid lane! Try again.")

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
            

# def change_lane_or_move(track: Track, driver: Driver, crash: int, gear: str) -> None:
#     """Ask the player whether to move forward or change lane for this driver."""
#     while True:
#         try:
#             choice = int(
#                 input('Choose action (1: move forward same lane, 2: move forward change lane): ')
#             )
#         except ValueError:
#             print('Invalid action! Try again')
#             continue
#         if choice in (1, 2):
#             break
#         print('Invalid action! Try again')
#     new_lane = None
#     if choice == 2:
#         tile = track.tile(driver.tile_idx)
#         while True:
#             try:
#                 new_lane = int(input('Enter lane change number (1, 2, 3): '))
#             except ValueError:
#                 print('Invalid lane change input! Try again.')
#                 continue
#             if 1 <= new_lane <= tile.lanes:
#                 break
#             print("Invalid lane! Try again.")
#     do_movement(track, driver, crash, gear, choice, new_lane)