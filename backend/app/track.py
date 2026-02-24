from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from track_json import find_track_json, load_track_json


@dataclass
class Square:
    lane: int                 # lane index (1..N)
    pos: int                  # square position within lane (1..K)
    inside: int               # inside rank (lower = more inside)

    # Optional rules read from JSON (see tracks/*.json)
    max_gear: Optional[int] = None
    max_gear_else_warning: Optional[int] = None

    max_gear_enter: Tuple[int, ...] = ()
    max_gear_enter_lane: Tuple[int, ...] = ()
    max_gear_exit: Tuple[int, ...] = ()
    max_gear_exit_lane: Tuple[int, ...] = ()

    enter_warning: Tuple[int, ...] = ()
    enter_warning_lane: Tuple[int, ...] = ()
    exit_warning: Tuple[int, ...] = ()
    exit_warning_lane: Tuple[int, ...] = ()

    merge: Optional[str] = None


@dataclass
class Tile:
    number: int  # matches JSON: "number": 1..N
    color: str
    lanes: int
    lane_squares: Dict[int, List[Square]] = field(default_factory=dict)

    def add_square(self, square: Square) -> None:
        """Add a Square to this tile."""
        self.lane_squares.setdefault(square.lane, []).append(square)

    def inside_priority_for_lane(self, lane: int) -> int:
        """Return inside priority for a lane (lower is more inside)."""
        squares = self.lane_squares.get(lane)
        if squares:
            return squares[0].inside
        return 100


@dataclass
class Track:
    name: str
    tiles: List[Tile] = field(default_factory=list)
    tile_by_number: Dict[int, Tile] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.load_from_json()

    @property
    def length(self) -> int:
        """Number of tiles on the track."""
        return len(self.tiles)

    def tile(self, index: int) -> Tile:
        """Get tile by 0-based index."""
        return self.tiles[index]

    def tile_num(self, number: int) -> Tile:
        """Get tile by JSON 'number' (1-based)."""
        try:
            return self.tile_by_number[number]
        except KeyError:
            raise KeyError(f"Invalid tile number {number}. Expected 1..{self.length}")

    def load_from_json(self) -> None:
        """Populate tiles from a JSON track definition (tracks/*.json)."""
        path = find_track_json(self.name)
        parsed = load_track_json(path)

        self.tiles.clear()
        self.tile_by_number.clear()

        for t in parsed.tiles:
            tile = Tile(number=t.number, color=t.color, lanes=len(t.lanes))

            for lane in t.lanes:
                for pos, sq in enumerate(lane.squares, start=1):
                    tile.add_square(
                        Square(
                            lane=lane.index,
                            pos=pos,
                            inside=sq.inside,
                            max_gear=sq.max_gear,
                            max_gear_else_warning=sq.max_gear_else_warning,
                            max_gear_enter=sq.max_gear_enter,
                            max_gear_enter_lane=sq.max_gear_enter_lane,
                            max_gear_exit=sq.max_gear_exit,
                            max_gear_exit_lane=sq.max_gear_exit_lane,
                            enter_warning=sq.enter_warning,
                            enter_warning_lane=sq.enter_warning_lane,
                            exit_warning=sq.exit_warning,
                            exit_warning_lane=sq.exit_warning_lane,
                            merge=sq.merge,
                        )
                    )

            self.tiles.append(tile)
            self.tile_by_number[tile.number] = tile

        # Make sure the internal list order matches tile numbers
        self.tiles.sort(key=lambda x: x.number)

    def print_track(self) -> None:
        """Debug-print the full track layout."""
        print(f"Track: {self.name} (tiles: {self.length})")
        for tile in self.tiles:
            print(f"Tile {tile.number} ({tile.color}): ", end="")
            for lane in range(1, tile.lanes + 1):
                squares = tile.lane_squares.get(lane, [])
                print(f"[Lane {lane}: {len(squares)} squares]", end="")
            print()


def prompt_tile_index(track: Track) -> int:
    """Prompt the user for a starting tile index (0..N-1).

    NOTE: the rest of the game stores tile_idx as 0-based.
    """
    while True:
        try:
            tile_num = int(input(f"Enter starting tile number (1 - {track.length}): "))
        except ValueError:
            print("Invalid tile! Try again.")
            continue

        if 1 <= tile_num <= track.length:
            return tile_num - 1
        print("Invalid tile! Try again.")


def prompt_lane_index(track: Track, tile_idx: int) -> int:
    """Prompt the user for a lane index on a given 0-based tile index."""
    tile = track.tile(tile_idx)
    while True:
        try:
            lane = int(input(f"Enter lane (1 - {tile.lanes}): "))
        except ValueError:
            print("Invalid lane! Try again.")
            continue

        if not (1 <= lane <= tile.lanes):
            print("Invalid lane! Try again.")
            continue

        if lane not in tile.lane_squares or not tile.lane_squares[lane]:
            print("Error: invalid or empty lane")
            continue

        return lane


def prompt_square_index(track: Track, tile_idx: int, lane_idx: int) -> int:
    """Prompt the user for a square index in a given lane on a 0-based tile index."""
    tile = track.tile(tile_idx)
    squares = tile.lane_squares.get(lane_idx, [])
    if not squares:
        print("Warning: lane has no squares, defaulting to 0")
        return 0

    max_idx = len(squares) - 1
    while True:
        try:
            sqr = int(input(f"Enter square index (0 - {max_idx}): "))
        except ValueError:
            print("Invalid square! Try again.")
            continue
        if 0 <= sqr <= max_idx:
            return sqr
        print("Invalid square! Try again.")