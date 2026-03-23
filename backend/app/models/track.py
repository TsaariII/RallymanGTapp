from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from backend.app.track_loader.track_json import find_track_json, load_track_json


@dataclass
class Square:
    """Square in a lane.
    data contains ONLY keys present in the JSON square object.
    """
    lane: int
    pos: int  # 1..K within lane
    data: Dict[str, Any]


@dataclass
class Tile:
    number: int
    color: str

    # Maximum lane index present in this tile (used for prompts/bounds).
    lanes: int

    # lane index -> list of squares
    lane_squares: Dict[int, List[Square]] = field(default_factory=dict)

    # merge_id -> anchor square (the square with real attributes, not just {"merge": ...})
    merge_anchors: Dict[str, Square] = field(default_factory=dict)

    def add_square(self, square: Square) -> None:
        self.lane_squares.setdefault(square.lane, []).append(square)

    def build_merge_anchors(self) -> None:
        """Build anchor map for merge placeholders inside this tile.
        Anchor: square has 'merge' AND has at least one other key (typically 'inside' and/or rules).
        Placeholder: square is exactly {'merge': 'Mx'}.
        We do NOT fail parsing if a placeholder has no same-tile anchor.
        Movement rules can decide what to do with that.
        """
        self.merge_anchors.clear()

        for squares in self.lane_squares.values():
            for sq in squares:
                mid = sq.data.get("merge")
                if not isinstance(mid, str) or not mid.strip():
                    continue
                if set(sq.data.keys()) == {"merge"}:
                    continue  # placeholder, not an anchor

                mid = mid.strip()
                prev = self.merge_anchors.get(mid)
                if prev is None:
                    self.merge_anchors[mid] = sq
                else:
                    if prev.data != sq.data:
                        raise ValueError(f"Tile {self.number}: conflicting anchors for merge id '{mid}'.")

    def effective_square(self, lane: int, square_idx: int) -> Square:
        """Return square to use for rules.
        If current square is a placeholder {'merge': 'Mx'} and an anchor exists, return the anchor.
        Otherwise return the square itself.
        """
        # print(F"effective_square lane: {lane}")
        # print(F"effective_square square: {square_idx}")
        sq = self.lane_squares[lane][square_idx]
        if set(sq.data.keys()) == {"merge"}:
            mid = str(sq.data["merge"]).strip()
            anchor = self.merge_anchors.get(mid)
            return anchor if anchor is not None else sq
        return sq

    def square_data(self, lane: int, square_idx: int) -> Dict[str, Any]:
        """What movement should use to check restrictions/warnings."""
        return self.effective_square(lane, square_idx).data

@dataclass
class Track:
    name: str
    tiles: List[Tile] = field(default_factory=list)
    tile_by_number: Dict[int, Tile] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.load_from_json()

    @property
    def length(self) -> int:
        return len(self.tiles)

    def tile(self, index: int) -> Tile:
        return self.tiles[index]

    def tile_num(self, number: int) -> Tile:
        try:
            return self.tile_by_number[number]
        except KeyError:
            raise KeyError(f"Invalid tile number {number}. Expected 1..{self.length}")

    def load_from_json(self) -> None:
        path = find_track_json(self.name)
        raw = load_track_json(path)

        self.tiles.clear()
        self.tile_by_number.clear()

        for t in raw["tiles"]:
            lanes_raw = t["lanes"]
            lane_ids = [int(l["index"]) for l in lanes_raw]
            lanes_max = max(lane_ids) if lane_ids else 0

            tile = Tile(number=int(t["number"]), color=str(t["color"]), lanes=lanes_max)

            for lane in lanes_raw:
                lane_idx = int(lane["index"])
                for pos, sq_obj in enumerate(lane["squares"], start=1):
                    tile.add_square(Square(lane=lane_idx, pos=pos, data=dict(sq_obj)))

            tile.build_merge_anchors()

            self.tiles.append(tile)
            self.tile_by_number[tile.number] = tile

        self.tiles.sort(key=lambda x: x.number)
        # self.print_track()

    def print_track(self) -> None:
        print(f"Track: {self.name} (tiles: {self.length})")
        for tile in self.tiles:
            print(f"Tile {tile.number} ({tile.color}): ", end="")
            for lane in range(1, tile.lanes + 1):
                squares = tile.lane_squares.get(lane, [])
                print(f"[Lane {lane}: {len(squares)} squares]", end="")
            print()


def prompt_tile_index(track: Track) -> int:
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
    tile = track.tile(tile_idx)
    squares = tile.lane_squares.get(lane_idx, [])
    if not squares:
        print("Warning: lane has no squares, defaulting to 0")
        return 0

    max_idx = len(squares)
    while True:
        try:
            sqr = int(input(f"Enter square index (1 - {max_idx}): ")) - 1
        except ValueError:
            print("Invalid square! Try again.")
            continue
        if 0 <= sqr <= max_idx:
            return sqr
        print("Invalid square! Try again.")