from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List


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


def load_track_json(path: Path) -> Dict[str, Any]:
    """Load + lightly validate a track JSON file.

    Goal: keep square objects as-is (exactly what exists in JSON).

    Square rules:
      - Anchor/normal square must include "inside".
      - Merge placeholder square must be exactly {"merge": "Mx"}.

    Everything else (gear limits, warnings) is left untouched and validated in gameplay logic.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Track JSON must be an object: {path}")

    name = raw.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"Track JSON missing/invalid 'name': {path}")

    tiles = raw.get("tiles")
    if not isinstance(tiles, list) or not tiles:
        raise ValueError(f"Track JSON missing/empty 'tiles': {path}")

    numbers: List[int] = []

    for t in tiles:
        if not isinstance(t, dict):
            raise ValueError(f"Tile must be an object: {path} -> {t!r}")

        if "number" not in t:
            raise ValueError(f"Tile missing 'number': {path} -> {t!r}")
        try:
            num = int(t["number"])
        except Exception:
            raise ValueError(f"Tile 'number' must be int: {path} -> {t.get('number')!r}")
        if num < 1:
            raise ValueError(f"Tile 'number' must be >= 1: {path} -> {num}")
        numbers.append(num)

        color = str(t.get("color", "")).strip().upper()
        if color not in {"Y", "O", "R"}:
            raise ValueError(f"Tile {num} has invalid 'color' {t.get('color')!r}: {path}")

        lanes = t.get("lanes")
        if not isinstance(lanes, list) or not lanes:
            raise ValueError(f"Tile {num} missing/empty 'lanes': {path}")

        lane_ids = set()
        for lane in lanes:
            if not isinstance(lane, dict):
                raise ValueError(f"Lane must be an object: {path} -> tile {num} -> {lane!r}")
            if "index" not in lane:
                raise ValueError(f"Lane missing 'index': {path} -> tile {num} -> {lane!r}")
            try:
                idx = int(lane["index"])
            except Exception:
                raise ValueError(f"Lane 'index' must be int: {path} -> tile {num} -> {lane.get('index')!r}")
            if idx < 1:
                raise ValueError(f"Lane 'index' must be >= 1: {path} -> tile {num} -> {idx}")
            if idx in lane_ids:
                raise ValueError(f"Duplicate lane index {idx} in tile {num}: {path}")
            lane_ids.add(idx)

            squares = lane.get("squares")
            if not isinstance(squares, list) or not squares:
                raise ValueError(f"Lane {idx} missing/empty 'squares': {path} -> tile {num}")

            for s in squares:
                if not isinstance(s, dict):
                    raise ValueError(f"Square must be an object: {path} -> tile {num} lane {idx} -> {s!r}")

                if "inside" in s:
                    try:
                        inside = int(s["inside"])
                    except Exception:
                        raise ValueError(
                            f"Square 'inside' must be int: {path} -> tile {num} lane {idx} -> {s.get('inside')!r}"
                        )
                    if inside < 1:
                        raise ValueError(
                            f"Square 'inside' must be >= 1: {path} -> tile {num} lane {idx} -> {inside}"
                        )
                else:
                    # placeholder must be exactly {"merge": "Mx"}
                    if set(s.keys()) != {"merge"}:
                        raise ValueError(
                            f"Square without 'inside' must be a pure merge placeholder {{'merge': ...}}. "
                            f"Got keys {sorted(s.keys())}: {path} -> tile {num} lane {idx}"
                        )
                    merge = s.get("merge")
                    if not isinstance(merge, str) or not merge.strip():
                        raise ValueError(
                            f"Merge placeholder must have non-empty string 'merge': {path} -> tile {num} lane {idx}"
                        )

    # sanity: contiguous numbering 1..N
    numbers_sorted = sorted(numbers)
    expected = list(range(1, len(numbers_sorted) + 1))
    if numbers_sorted != expected:
        raise ValueError(f"Tile numbers must be contiguous starting at 1. Got {numbers_sorted} in {path}")

    return raw