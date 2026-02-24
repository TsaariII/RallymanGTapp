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
    
    # def check_movement(self, track: Track) -> None:
    #     """Validate movement to the next square"""
    #     if 

    def move_forward(self, track: Track) -> None:
        """Move the driver one square forward along the current lane."""
        tile = track.tile(self.tile_idx)
        lane_squares = tile.lane_squares.get(self.lane_idx)
        if not lane_squares:
            print("Error: driver is in a non-existing or empty lane!")
            return
        # self.check_movement(track)
        if self.square_idx + 1 < len(lane_squares):
            self.square_idx += 1
            return
        self.tile_idx += 1
        if self.tile_idx >= track.length:
            self.lap += 1
            self.tile_idx = 0
        next_tile = track.tile(self.tile_idx)
        next_lane_squares = next_tile.lane_squares.get(self.lane_idx)
        if not next_lane_squares:
            print(f"Error: lane {self.lane_idx} does not exist in tile {self.tile_idx}!")
            return
        self.square_idx = 0
        print(
            f"{self.name} moved to tile {self.tile_idx + 1}"
            f"({next_tile.color}) in lane {self.lane_idx}"
        )

    def change_lane(self, track: Track) -> None:
        """Change lane left or right on the current tile."""
        tile = track.tile(self.tile_idx)
        while True:
            try:
                direction = int(
                    input('Enter lane change direction (1: left, -1: right): ')
                )
            except ValueError:
                print('Invalid lane change input! Try again.')
                continue
            new_lane = self.lane_idx + direction
            print(f"new lane: {new_lane}")
            if 1 <= new_lane <= tile.lanes:
                self.lane_idx = new_lane
                print(f"{self.name} switched to lane {self.lane_idx}")
                break
            print("Invalid lane! Try again.")

def change_lane_or_move(track: Track, driver: Driver) -> None:
    """Ask the player whether to move forward or change lane for this driver."""
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
    if choice == 1:
        driver.move_forward(track)
    else:
        driver.change_lane(track)