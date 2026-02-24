from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRACKS_DIR = PROJECT_ROOT / "tracks"


def _slugify(name: str) -> str:
    """Convert 'Albert Park' -> 'albert_park'."""
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def find_track_json(track_name: str, tracks_dir: Path = TRACKS_DIR) -> Path:
    """Resolve a track JSON path.

    Rules:
      1) Try tracks/<slug>.json
      2) Otherwise scan tracks/*.json and match by top-level 'name' (case-insensitive)
    """
    tracks_dir = tracks_dir.resolve()
    if not tracks_dir.exists():
        raise FileNotFoundError(f"Tracks directory not found: {tracks_dir}")

    slug_path = tracks_dir / f"{_slugify(track_name)}.json"
    if slug_path.exists():
        return slug_path

    for p in sorted(tracks_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict) and str(data.get("name", "")).strip().lower() == track_name.strip().lower():
            return p

    raise FileNotFoundError(
        f"Track '{track_name}' not found. Expected {slug_path} or a JSON with name='{track_name}' under {tracks_dir}"
    )


def _as_int_list(
    v: Any,
    *,
    field: str,
    path: Path,
    tile_num: int,
    lane_idx: int,
    square_pos: int,
    min_val: int,
    max_val: Optional[int] = None,
) -> List[int]:
    """Accept int or list[int]; return list[int]."""
    if v is None:
        return []
    seq: Sequence[Any]
    if isinstance(v, list):
        seq = v
    else:
        seq = [v]

    out: List[int] = []
    for item in seq:
        try:
            n = int(item)
        except Exception:
            raise ValueError(
                f"{field} must be int or list[int] (got {item!r}) in tile {tile_num} lane {lane_idx} square {square_pos} in {path}"
            )
        if n < min_val:
            raise ValueError(
                f"{field} must be >= {min_val} (got {n}) in tile {tile_num} lane {lane_idx} square {square_pos} in {path}"
            )
        if max_val is not None and n > max_val:
            raise ValueError(
                f"{field} must be <= {max_val} (got {n}) in tile {tile_num} lane {lane_idx} square {square_pos} in {path}"
            )
        out.append(n)
    return out


def _as_opt_int_singleton(
    v: Any,
    *,
    field: str,
    path: Path,
    tile_num: int,
    lane_idx: int,
    square_pos: int,
    min_val: int,
    max_val: Optional[int] = None,
) -> Optional[int]:
    """Accept int or [int]; return int or None."""
    if v is None:
        return None
    vals = _as_int_list(
        v,
        field=field,
        path=path,
        tile_num=tile_num,
        lane_idx=lane_idx,
        square_pos=square_pos,
        min_val=min_val,
        max_val=max_val,
    )
    if len(vals) != 1:
        raise ValueError(
            f"{field} must be a single int (or single-element list) in tile {tile_num} lane {lane_idx} square {square_pos} in {path}"
        )
    return vals[0]


@dataclass(frozen=True)
class ParsedSquare:
    inside: int

    # Base restriction on this square
    max_gear: Optional[int] = None

    # "If not <= this gear, add ⚠️" style
    max_gear_else_warning: Optional[int] = None

    # Conditional restrictions / warnings tied to lane transitions
    max_gear_enter: Tuple[int, ...] = ()
    max_gear_enter_lane: Tuple[int, ...] = ()
    max_gear_exit: Tuple[int, ...] = ()
    max_gear_exit_lane: Tuple[int, ...] = ()

    enter_warning: Tuple[int, ...] = ()
    enter_warning_lane: Tuple[int, ...] = ()
    exit_warning: Tuple[int, ...] = ()
    exit_warning_lane: Tuple[int, ...] = ()

    merge: Optional[str] = None


@dataclass(frozen=True)
class ParsedLane:
    index: int
    squares: List[ParsedSquare]


@dataclass(frozen=True)
class ParsedTile:
    number: int
    color: str
    lanes: List[ParsedLane]


@dataclass(frozen=True)
class ParsedTrack:
    name: str
    tiles: List[ParsedTile]


def load_track_json(path: Path) -> ParsedTrack:
    """Parse + validate a track JSON file.

    Supports two square formats:
      - legacy: squares: [1, 1, 2, ...]
      - object: squares: [{"inside": 1, "max_gear": 2, ...}, ...]

    Note: some merge placeholder squares may omit "inside"; we fill it from the previous square in that lane,
    or fallback to the lane index.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid track JSON (expected object) in {path}")

    name = str(raw.get("name", "")).strip()
    if not name:
        raise ValueError(f"Track JSON missing 'name' in {path}")

    raw_tiles = raw.get("tiles")
    if not isinstance(raw_tiles, list) or not raw_tiles:
        raise ValueError(f"Track JSON missing/empty 'tiles' in {path}")

    tiles: List[ParsedTile] = []
    seen_numbers = set()

    for t in raw_tiles:
        if not isinstance(t, dict):
            raise ValueError(f"Invalid tile entry in {path}: {t!r}")

        number_raw = t.get("number", None)
        if number_raw is None:
            raise ValueError(f"Tile missing 'number' in {path}: {t!r}")

        number = int(number_raw)
        if number < 1:
            raise ValueError(f"Invalid tile number {number} in {path}")

        if number in seen_numbers:
            raise ValueError(f"Duplicate tile number {number} in {path}")
        seen_numbers.add(number)

        color = str(t.get("color", "")).strip().upper()
        if color not in {"Y", "O", "R"}:
            raise ValueError(f"Invalid tile color '{color}' at number {number} in {path}")

        raw_lanes = t.get("lanes")
        if not isinstance(raw_lanes, list) or not raw_lanes:
            raise ValueError(f"Tile {number} missing/empty 'lanes' in {path}")

        lanes: List[ParsedLane] = []
        lane_indices = set()

        for l in raw_lanes:
            if not isinstance(l, dict):
                raise ValueError(f"Invalid lane entry in tile {number} in {path}: {l!r}")

            idx_raw = l.get("index", None)
            if idx_raw is None:
                raise ValueError(f"Lane missing 'index' in tile {number} in {path}: {l!r}")

            idx = int(idx_raw)
            if idx < 1:
                raise ValueError(f"Invalid lane index {idx} in tile {number} in {path}")

            if idx in lane_indices:
                raise ValueError(f"Duplicate lane index {idx} in tile {number} in {path}")
            lane_indices.add(idx)

            raw_squares = l.get("squares")
            if not isinstance(raw_squares, list) or not raw_squares:
                raise ValueError(f"Lane {idx} in tile {number} missing/empty 'squares' in {path}")

            squares: List[ParsedSquare] = []
            last_inside: Optional[int] = None

            for square_pos, s in enumerate(raw_squares, start=1):
                # legacy int format
                if isinstance(s, (int, float, str)) and not isinstance(s, dict):
                    try:
                        inside = int(s)
                    except Exception:
                        raise ValueError(f"Non-integer square value {s!r} in tile {number} lane {idx} in {path}")
                    if inside < 1:
                        raise ValueError(f"Invalid square inside-rank {inside} in tile {number} lane {idx} in {path}")
                    squares.append(ParsedSquare(inside=inside))
                    last_inside = inside
                    continue

                if not isinstance(s, dict):
                    raise ValueError(
                        f"Invalid square entry (expected int or object) {s!r} in tile {number} lane {idx} in {path}"
                    )

                # object format
                inside_raw = s.get("inside", None)
                if inside_raw is None:
                    # merge placeholder square: infer inside
                    inside = last_inside if last_inside is not None else idx
                else:
                    try:
                        inside = int(inside_raw)
                    except Exception:
                        raise ValueError(
                            f"'inside' must be int (got {inside_raw!r}) in tile {number} lane {idx} square {square_pos} in {path}"
                        )

                if inside < 1:
                    raise ValueError(
                        f"'inside' must be >= 1 (got {inside}) in tile {number} lane {idx} square {square_pos} in {path}"
                    )

                max_gear = _as_opt_int_singleton(
                    s.get("max_gear"),
                    field="max_gear",
                    path=path,
                    tile_num=number,
                    lane_idx=idx,
                    square_pos=square_pos,
                    min_val=0,
                    max_val=6,
                )

                max_gear_else_warning = _as_opt_int_singleton(
                    s.get("max_gear_else_warning"),
                    field="max_gear_else_warning",
                    path=path,
                    tile_num=number,
                    lane_idx=idx,
                    square_pos=square_pos,
                    min_val=0,
                    max_val=6,
                )

                max_gear_enter = tuple(
                    _as_int_list(
                        s.get("max_gear_enter"),
                        field="max_gear_enter",
                        path=path,
                        tile_num=number,
                        lane_idx=idx,
                        square_pos=square_pos,
                        min_val=0,
                        max_val=6,
                    )
                )
                max_gear_enter_lane = tuple(
                    _as_int_list(
                        s.get("max_gear_enter_lane"),
                        field="max_gear_enter_lane",
                        path=path,
                        tile_num=number,
                        lane_idx=idx,
                        square_pos=square_pos,
                        min_val=1,
                    )
                )

                max_gear_exit = tuple(
                    _as_int_list(
                        s.get("max_gear_exit"),
                        field="max_gear_exit",
                        path=path,
                        tile_num=number,
                        lane_idx=idx,
                        square_pos=square_pos,
                        min_val=0,
                        max_val=6,
                    )
                )
                max_gear_exit_lane = tuple(
                    _as_int_list(
                        s.get("max_gear_exit_lane"),
                        field="max_gear_exit_lane",
                        path=path,
                        tile_num=number,
                        lane_idx=idx,
                        square_pos=square_pos,
                        min_val=1,
                    )
                )

                enter_warning = tuple(
                    _as_int_list(
                        s.get("enter_warning"),
                        field="enter_warning",
                        path=path,
                        tile_num=number,
                        lane_idx=idx,
                        square_pos=square_pos,
                        min_val=0,
                    )
                )
                enter_warning_lane = tuple(
                    _as_int_list(
                        s.get("enter_warning_lane"),
                        field="enter_warning_lane",
                        path=path,
                        tile_num=number,
                        lane_idx=idx,
                        square_pos=square_pos,
                        min_val=1,
                    )
                )
                exit_warning = tuple(
                    _as_int_list(
                        s.get("exit_warning"),
                        field="exit_warning",
                        path=path,
                        tile_num=number,
                        lane_idx=idx,
                        square_pos=square_pos,
                        min_val=0,
                    )
                )
                exit_warning_lane = tuple(
                    _as_int_list(
                        s.get("exit_warning_lane"),
                        field="exit_warning_lane",
                        path=path,
                        tile_num=number,
                        lane_idx=idx,
                        square_pos=square_pos,
                        min_val=1,
                    )
                )

                def _pair_check(a: Tuple[int, ...], b: Tuple[int, ...], a_name: str, b_name: str) -> None:
                    if a and b and len(a) != len(b):
                        raise ValueError(
                            f"{a_name} and {b_name} length mismatch in tile {number} lane {idx} square {square_pos} in {path}"
                        )

                _pair_check(max_gear_enter, max_gear_enter_lane, "max_gear_enter", "max_gear_enter_lane")
                _pair_check(max_gear_exit, max_gear_exit_lane, "max_gear_exit", "max_gear_exit_lane")
                _pair_check(enter_warning, enter_warning_lane, "enter_warning", "enter_warning_lane")
                _pair_check(exit_warning, exit_warning_lane, "exit_warning", "exit_warning_lane")

                merge = s.get("merge")
                if merge is not None:
                    merge = str(merge).strip()
                    if not merge:
                        merge = None

                squares.append(
                    ParsedSquare(
                        inside=inside,
                        max_gear=max_gear,
                        max_gear_else_warning=max_gear_else_warning,
                        max_gear_enter=max_gear_enter,
                        max_gear_enter_lane=max_gear_enter_lane,
                        max_gear_exit=max_gear_exit,
                        max_gear_exit_lane=max_gear_exit_lane,
                        enter_warning=enter_warning,
                        enter_warning_lane=enter_warning_lane,
                        exit_warning=exit_warning,
                        exit_warning_lane=exit_warning_lane,
                        merge=merge,
                    )
                )

                last_inside = inside

            lanes.append(ParsedLane(index=idx, squares=squares))

        lanes.sort(key=lambda x: x.index)
        tiles.append(ParsedTile(number=number, color=color, lanes=lanes))

    tiles.sort(key=lambda x: x.number)

    # enforce contiguous numbering 1..N
    expected = list(range(1, len(tiles) + 1))
    actual = [t.number for t in tiles]
    if actual != expected:
        raise ValueError(f"Tile numbers must be contiguous starting at 1. Got {actual} in {path}")

    return ParsedTrack(name=name, tiles=tiles)