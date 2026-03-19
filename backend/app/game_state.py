"""
Game State Management — serialize / deserialize a Game to plain dicts.
 
v1: in-memory store mapping game_id (UUID str) → Game instance.
Later: swap in Redis, SQLite, or Postgres without touching callers.
 
Usage:
    from game_state import GameStore, serialize_game, deserialize_game
 
    store = GameStore()
    game_id = store.create(game)          # returns UUID string
    game     = store.get(game_id)         # returns Game or raises
    store.save(game_id, game)             # update after mutations
    snapshot = serialize_game(game)       # plain dict, JSON-safe
    game     = deserialize_game(snapshot) # rebuild from dict
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional
from enums import Tires, TireCondition, Weather
from tire import Tire
from stats import Stats
from driver import Driver
from team import Team
from track import Track
from game import Game
from dice import create_dice

def serialize_stats(stats: Stats) -> Dict[str, Any]:
    """Snapshot a Stats object into a plain dict."""
    return {
        'turns': stats.turns,
        'focus_tokens': stats.focus_tokens,
        'used_focus_tokens': stats.used_focus_tokens,
        'lost_gear': stats.lost_gear,
        'lost_brake': stats.lost_brake,
        'lost_coast': stats.lost_coast,
        'weather_token': stats.weather_token,
        'yellow_flag': stats.yellow_flag,
        'green_flag': stats.green_flag,
        'total_time': stats.total_time,
        'lap_times': list(stats.lap_time),
        'dice_rolls': list(stats.dice_rolls)
    }

def desrialize_stats(data: Dict[str, Any]) -> Stats:
    """Rebuild a Stats object from a plain dict."""
    s = Stats()
    s.turns = data['turns']
    s.focus_tokens = data['focus_tokens']
    s.used_focus_tokens = data['used_focus_tokens']
    s.lost_gear = data['lost_gear']
    s.lost_brake = data['lost_break']
    s.lost_coast = data['lost_coast']
    s.weather_token = data['weather_token']
    s.yellow_flag = data['yellow_flag']
    s.green_flag = data['green_flag']
    s.total_time = data['total_time']
    s.lap_time = list(data['lap_time'])
    s.dice_rolls = list(data['dice_rolls'])
    return s

def serialize_tires(tire: Tire) -> Dict[str, Any]:
    """Snapshot a Tire object into a plain dict."""
    return {
        'type': tire.type,
        'weather': tire.weather,
        'turns': tire.turns,
        'condition': tire.condition
    }

def deserialize_tires(data: Dict[str, Any]) -> Tire:
    """Rebuild a Tire from a plain dict."""
    tire = Tire(
        type=Tires(data['type']),
        weather=Weather(data['weather']),
        turns=data['turns'],
        condition=TireCondition(data['condition'])
    )
    return tire

def serialize_driver(driver: Driver) -> Dict[str, Any]:
    """Snapshot a Driver into a plain dict."""
    return {
        'name': driver.name,
        'team': driver.team,
        'position': driver.position,
        'current_gear': driver.current_gear,
        'lap': driver.lap,
        'tile_idx': driver.tile_idx,
        'lane_idx': driver.lane_idx,
        'square_idx': driver.square_idx,
        'inside_idx': driver.inside_idx,
        'starting_tile': driver.starting_tile,
        'tires': serialize_tires(driver.tires),
        'stats': serialize_stats(driver.stats)
    }

def deserialize_driver(data: Dict[str, Any], weather: Weather) -> Driver:
    """Rebuild a Driver from a plain dict."""
    tires = data['tires']
    tires_enum = Tires(tires['type'])
    driver = Driver(
        name=data['name'],
        team=data['team'],
        tires=tires_enum,
        weather=weather
    )
    driver.position = data['position']
    driver.current_gear = data['current_gear']
    driver.lap = data['lap']
    driver.tile_idx = data['tile_idx']
    driver.lane_idx = data['lane_idx']
    driver.square_idx = data['square_idx']
    driver.inside_idx = data['inside_idx']
    driver.starting_tile = data['starting_tile']
    driver.tires = deserialize_tires(tires)
    driver.stats = desrialize_stats(data['stats'])
    return driver

def serialize_team(team: Team) -> Dict[str, Any]:
    """Snapshot a Team into a plain dict.
 
    Drivers are serialized by reference to their names — the full driver
    state lives in the top-level drivers list of the game snapshot.
    We store the team name and its driver names so we can re-link them
    during deserialization.
    """
    return {
        'name': team.name,
        'drivers': [d.name for d in team.drivers]
    }

def serialize_game(game: Game) -> Dict[str, Any]:
    """Create a JSON-safe snapshot of the entire Game.
 
    The snapshot contains everything needed to rebuild the Game object
    from scratch: track name, weather, teams, drivers (with full state),
    and the dice configuration (which is deterministic from the face set,
    so we just note which faces exist).
    """
    return {
        'track': game.track.name,
        'weather': game.weather.value,
        'teams': [serialize_team(t) for t in game.teams],
        'drivers': [serialize_driver(d) for d in game.drivers],
        'dices': list(game.dices.keys())
    }

def deserialize_game(data: Dict[str, Any]) -> Game:
    """Rebuild a full Game object from a serialized snapshot.
 
    This re-loads the track from JSON (same as Game.__init__ does),
    sets weather, reconstructs drivers with their exact state, and
    re-links teams to drivers.
    """
    name = data['name']
    weather = Weather(data['weather'])
    game = Game(name)
    game.weather = weather
    game.dices = {
        face: create_dice(face)
        for face in data.get('dice_faces', ['1', '2', '3', '4', '5', '6', 'C', 'B'])
    }
    drivers_data: Dict[str, Driver] = {}
    for d in data['drivers']:
        driver = deserialize_driver(d, weather)
        drivers_data[driver.name] = driver
    game.drivers = list(drivers_data.values())
    game.teams = []
    for t in data['teams']:
        t_name = t['name']
        d_names = t['drivers']
        team = Team.__new__(Team)
        team.name = t_name
        team.drivers = [drivers_data[n] for n in d_names]
        game.teams.append(team)
    return game

class GameState:
    """In-memory store: game_id → Game instance.
 
    Thread-safety note: this is *not* thread-safe. For a dev server
    running with a single worker that's fine.
    """
    def __init__(self) -> None:
        self._games: Dict[str, Game] = {}
        self._snapshots: Dict[str, Dict[str, Any]] = {}

    def create(self, game: Game) -> str:
        """Store a Game and return a new UUID game_id."""
        id = str(uuid.uuid4())
        self._games[id] = game
        self._snapshots[id] = serialize_game(game)
        return id
    
    def get(self, id: str) -> Game:
        """Retrieve a live Game instance. Raises KeyError if not found."""
        if id not in self._games:
            raise KeyError(f"Game '{id}' not found")
        return self._games[id]

    def save(self, id: str) -> None:
        """Re-snapshot the current Game state.
 
        Call this after any mutation (turn, round, position change)
        so the snapshot stays in sync."""
        game = self.get(id)
        self._snapshots[id] = serialize_game(game)

    def snapshot(self, id: str) -> Dict[str, Any]:
        """Return the latest serialized snapshot for a game."""
        if id not in self._snapshots:
            raise KeyError(f"Game '{id}' not found")
        return self._snapshots[id]

    def restore(self, id: str) -> Game:
        """Rebuild a Game from its last saved snapshot.
 
        Useful if the live Game instance got corrupted or you want to
        roll back to the last save point.
        """
        snapshot = self.snapshot(id)
        game = deserialize_game(snapshot)
        self._games[id] = game
        return game

    def delete(self, id: str) -> None:
        """Remove a game from the store entirely."""
        self._games.pop(id, None)
        self._snapshots.pop(id, None)

    def list_games(self) -> List[Dict[str, Any]]:
        """Return summary info for all active games."""
        result = []
        for id, game in self._games.items():
            result.append({
               'id': id,
               'track': game.track.name,
               'weather': game.weather.value,
               'teams': [t.name for t in game.teams],
               'drivers': [d.name for d in game.drivers]
            })
        return result