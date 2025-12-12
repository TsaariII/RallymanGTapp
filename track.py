
from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Square:
    lane: int
    pos: int
    inside: int

@dataclass
class Tile:
    def __init__(self, color: str, lanes: int) -> None:
        self.color = color
        self.lanes = lanes
        self.lane_squares: Dict[int, List[Square]] = {}

    def add_square(self, lane: int, pos: int, inside: int) -> None:
         """Add a square to a lane on this tile."""
         if lane not in self.lane_squares:
            self.lane_squares.setdefault(lane, []).append(
            Square(lane=lane, pos=pos, inside=inside)
         )

    def inside_priority_for_lane(self, lane: int) -> int:
        """Return inside priority for a lane; higher means more outside."""
        squares = self.lane_squares.get(lane)
        if squares:
            return squares[0].inside
        return 100

@dataclass
class Track:
    name: str
    tiles: List[Tile] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.load_from_database("tracks.db")

    @property
    def length(self) -> int:
        """Number of tiles on the track."""
        return len(self.tiles)
    
    def tile(self, index: int) -> Tile:
        """Get tile at given index."""
        return self.tiles[index]
    
    def load_from_database(self, db_name: str) -> None:
        """Populate tiles from the SQLite database."""
        try:
            with sqlite3.connect(db_name) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, position, color, lanes
                    FROM tiles
                    WHERE track_id = (SELECT id FROM tracks WHERE name = ?)
                    ORDER BY position
                    """, [self.name]
                )
                tile_rows = cur.fetchall()
                if not tile_rows:
                    print(f"No tiles found for track '{self.name}'.")
                    return
                for tile_id, position, color, lanes in tile_rows:
                    tile = Tile(color=color, lanes=lanes)
                    cur.execute(
                        """
                        SELECT lane, position, inside_lane
                        FROM squares
                        WHERE tile_id = ?
                        ORDER BY lane, position
                        """, [tile_id]
                    )
                    for lane, pos, inside_lane in cur.fetchall():
                        tile.add_square(lane=lane, pos=pos, inside=inside_lane)
                    self.tiles.append(tile)
        except sqlite3.Error as e:
                print(f"Can't open database '{db_name}': {e}")
        
        def print_track(self) -> None:
            """Debug-print the full track layout."""
            print(f"Track: {self.name} (length: {self.length})")
            for i, tile in enumerate(self.tiles):
                print(f"Tile {i} ({tile.color}): ", end="")
                for lane, squares in tile.lane_squares.items():
                    print(f"[Lane {lane}: {len(squares)} squares]", end="")
                print()

def prompt_tile_index(track: Track) -> int:
    """Prompt the user for a starting tile index."""
    while True:
        try:
            tile_idx = int(
                input(f"Enter starting tile (0 - {track.length - 1}): ")
            )
        except ValueError:
            print('Invalid tile! Try again.')
            continue
        if 0 <= tile_idx < track.length:
            return tile_idx
        print('Invalid tile! Try again.')

def prompt_lane_index(track: Track, tile_idx: int) -> int:
    """Prompt the user for a lane index on a given tile."""
    tile = track.tile(tile_idx)
    while True:
        try:
            lane = int(input(f"Enter lane (1 - {tile.lanes}): "))
        except ValueError:
            print('Invalid lane! Try again.')
            continue
        if not (1 <= lane <= tile.lanes):
            print('Invalid lane! Try again.')
            continue
        if lane not in tile.lane_squares or not tile.lane_squares[lane]:
            print('Error: invalid or empty lane')
            continue
        return lane

def prompt_square_index(track: Track, tile_idx: int, lane_idx: int) -> int:
    """Prompt the user for a square index in a given lane on a tile."""
    tile = track.tile(tile_idx)
    squares = tile.lane_squares.get(lane_idx, [])
    if not squares:
        print('Warning: lane has no squares, defaulting to 0')
        return 0
    max_idx = len(squares) - 1
    while True:
        try:
            sqr = int(f"Enter square index (0 - {max_idx}): ")
        except ValueError:
            print('Invalid square! Try again.')
            continue
        if 0 <= sqr <= max_idx:
            return sqr
        print('Invalid square! Try again.')