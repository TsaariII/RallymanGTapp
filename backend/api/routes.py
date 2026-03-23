"""
Rallyman GT — FastAPI routes.
 
Each endpoint maps directly to an existing Game method:
 
    CLI step                     →  Endpoint
    ─────────────────────────────────────────────────────────────
    Game(track_name)             →  POST   /games
    game.add_team(...)           →  POST   /games/{id}/teams
    game.set_tires(...)          →  PUT    /games/{id}/tires
    game.set_starting_positions  →  PUT    /games/{id}/positions
    driver_turn (one-by-one)     →  POST   /games/{id}/turns
    all_at_once + apply          →  POST   /games/{id}/turns/aao
    check_positions / standings  →  GET    /games/{id}/standings
    get_driver_state             →  GET    /games/{id}/drivers/{name}
    —                            →  GET    /games/{id}
    —                            →  GET    /games
    —                            →  DELETE /games/{id}
    find_track_json + load       →  GET    /tracks/{name}
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

_THIS_FILE = Path(__file__).resolve()
_API_DIR = _THIS_FILE.parent
_BACKEND_DIR = _API_DIR.parent
_APP_DIR = _BACKEND_DIR / "app"
_MODELS_DIR = _APP_DIR / "models"
_REPO_ROOT = _BACKEND_DIR.parent

for p in [str(_REPO_ROOT), str(_APP_DIR), str(_MODELS_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.models.game import Game
from app.models.enums import Weather, Tires
from app.models.dice import (
    StepAction,
    random_roll,
    all_at_once,
    apply_all_at_once_moves
)
from app.state.game_state import GameState, serialize_game
from app.track_loader.track_json import find_track_json, load_track_json

router = FastAPI(title='Rallyman GT', version='0.1.0')
store = GameState()

# POST /games
class CreateGameRequest(BaseModel):
    track: str = Field(..., description='Track name')
    weather: str = Field('Dry', description='Dry or Wet')

class CreateGameResponse(BaseModel):
    id: str
    track: str
    weather: str

# POST /games/{id}/teams
class Team:
    name: str
    driver1: str
    driver2: str
    tires: str = 'Normal'

class AddTeamsRequest(BaseModel):
    teams: List[Team]

# PUT /games/{id}/tires
class SetTiresRequest(BaseModel):
    name: str
    tire: str

# PUT /games/{id}/positions
class SetPositionsRequest(BaseModel):
    name: str
    position: int = Field(..., ge=1, le=12)
    tile: int
    lane: int
    sqr: int

# POST /games/{id}/turns
class StepActionModel(BaseModel):
    choice: int = 1
    new_lane: Optional[int] = None

class TurnRequest(BaseModel):
    name: str
    dice: List[str]
    actions: List[StepActionModel] = []

# POST /games/{id}/turns/aao
class AllAtOnceRequest(BaseModel):
    name: str
    dice: List[str]

class AllAtOnceLocationRequest(BaseModel):
    name: str
    tile: int
    lane: int
    sqr: int
    final_gear: Optional[str] = None

def _get_game(id: str) -> Game:
    """Fetch game from store or raise 404."""
    try:
        return store.get(id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Game '{id}' not found")

def _parse_weather(value: str) -> Weather:
    try:
        return Weather(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid weather '{value}'. Must be Dry or Wet.")

def _parse_tires(value: str) -> Tires:
    try:
        return Tires(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tire type '{value}'. Must be 'Normal', 'Sprint', or 'Wet'.")


@router.get('/tracks/{name}')
def get_track(name: str) -> Dict[str, Any]:
    """Return raw track JSON for the frontend to render the board.
    """
    try:
        path = find_track_json(name)
        return load_track_json(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/games')
def list_games() -> List[Dict[str, Any]]:
    """List all active games (summary only)."""
    return store.list_games()

@router.post('/games', status_code=201)
def create_game(body: CreateGameRequest) -> CreateGameRequest:
    """Create a new game.
    Returns the game_id you'll use for every subsequent call.
    """
    weather = _parse_weather(body.weather)
    try:
        game = Game(body.track)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    game.set_weather(weather)
    id = store.create(game)
    return CreateGameRequest(id=id, track=body.track, weather=body.weather)

@router.get('/games/{game_id}')
def get_game(id:str) -> Dict[str, Any]:
    """Return the full serialized game snapshot."""
    game = _get_game(id)
    store.save(id)
    return store.snapshot(id)

@router.delete('/games/{game_id}', status_code=204)
def delete_game(id: str) -> None:
    """Remove a game from the store."""
    _get_game(id)
    store.delete(id)

@router.post('/games/{game_id}/teams')
def add_teams(id: str, body: AddTeamsRequest) -> Dict[str, Any]:
    """Add one or more teams to the game.
    Each team creates two drivers automatically.
    """
    game = _get_game(id)
    added = []
    for t in body.teams:
        tires = _parse_tires(t.tires)
        try:
            team = game.add_team(t.name, t.driver1, t.driver1, tires)
            added.append({
                'team': t.name,
                'drivers': [d.name for d in team.drivers]
            })
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    store.save(id)
    return {'teams': added, 'total_drivers': len(game.drivers)}

@router.put('/games/{game_id}/tires')
def set_tires(id: str, body: SetTiresRequest) -> Dict[str, Any]:
    """Change tire type for a specific driver."""
    game = _get_game(id)
    tires = _parse_tires(body.tire)
    try:
        game.set_tires(body.name, tires)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    store.save(id)
    d_state = game.get_driver_state(body.name)
    return {
        'name': body.name,
        'tires': d_state['tires']
    }

@router.put('/games/{game_id}/positions')
def set_positions(id: str, body: SetPositionsRequest) -> Dict[str, Any]:
    """Set a driver's starting grid position and on-track location.
    The tile is 0-indexed (tile 1 in JSON = index 0 here).
    """
    game = _get_game(id)
    try:
        game.set_starting_positions(
            name=body.name,
            position=body.position,
            tile_idx=body.tile,
            lane_idx=body.lane,
            square_idx=body.sqr
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    store.save(id)
    return game.get_driver_state(body.name)

@router.post('/games/{game_id}/turns')
def execute_turn(id: str, body: TurnRequest) -> Dict[str, Any]:
    """Execute a single driver's turn in one-by-one mode.

    The dice are rolled server-side. Actions (forward / lane-change) are
    provided up-front — one per non-brake die in the sequence.
 
    Returns the full step-by-step log, final position, and crash info.
    """
    game = _get_game(id)
    input = game.parse_input(','.join(body.dice))
    if not input:
        raise HTTPException(status_code=400, detial=f"Invalid dice sequence: {body.dice}")
    actions = [StepAction(choice=a.choice, new_lane=a.new_lane) for a in body.actions]
    try:
        result = game.driver_turn(
            name=body.name,
            dices=input,
            actions=actions,
            roll_provider=random_roll
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detial=str(e))
    store.save(id)
    return {
        'name': result.name,
        'gear_after': result.gear_after,
        'lost_control': result.lost_control,
        'crash': result.results.crash,
        'stopped_early': result.results.stopped_early,
        'steps': result.results.steps,
        'position_after': result.pos_after,
        'driver_state': game.get_driver_state(body.name)
    }

# Step 1: roll all dice (no movement yet)
router.post('/games/{game_id}/turns/aao/roll')
def all_at_once_roll(id: str, body: AllAtOnceRequest) -> Dict[str, Any]:
    """Roll all dice at once — returns rolls and available moves.
 
    After this, the client shows the results and lets the player pick
    a landing square, then calls POST .../aao/place.
    """
    game = _get_game(id)
    input = game.parse_input(','.join(body.dice))
    if not input:
        raise HTTPException(status_code=400, detail=f"Invalid dice sequence: {body.dice}")
    try:
        driver = game._find_driver(body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    result = all_at_once(
        seq=input,
        dices=game.dices,
        driver=driver,
        track=game.track,
        roll_provider=random_roll
    )
    # Stash the result on the game so the place step can use it.
    # Simple approach; for multi-user needs to use a proper cache.
    game._pending_aao[body.name] = result
    store.save(id)
    return {
        'name': body.name,
        'rolls': result.rolls,
        'crash': result.crash,
        'lost_control': result.lost_control,
        'moves': result.moves,
        'focus_tokens': result.focus_tokens,
        'final_gear': result.final_gear,
        'penalty_gear': result.penalty_gear
    }

# Step 2: place the driver after seeing rolls
@router.post('/games/{game_id}/turns/aao/place')
def all_at_once_place(id: str, body: AllAtOnceLocationRequest) -> Dict[str, Any]:
    """Place the driver after an all-at-once roll.
    """
    game = _get_game(id)
    pending = getattr(game, '_pending_aao', {})
    result = pending.get(body.name)
    if result is None:
        raise HTTPException(status_code=400, detail=f"No pending all-at-once roll for driver '{body.driver}'. "f"Call POST .../aao/roll first.")
    try:
        driver = game._find_driver(body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        routerly_all_at_once_moves(
            aao_result=result,
            driver=driver,
            track=game.track,
            tile_idx=body.tile,
            lane_idx=body.lane,
            square_idx=body.sqr
        )
    except (ValueError, IndexError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    driver.stats.turns += 1
    driver.stats.add_lap_time(driver.current_gear)
    pending.pop(body.name, None)
    store.save(id)
    return game.get_driver_state(body.name)

@router.get('/games/{game_id}/standings')
def get_standings(id: str) -> List[Dict[str, Any]]:
    """Current race standings.
    Calls game.get_standings() which internally runs check_positions().
    """
    game = _get_game(id)
    return game.get_standings()

@router.get('/games/{game_id}/drivers/{name}')
def get_driver(id: str, name: str) -> Dict[str, Any]:
    """Full state of a single driver."""
    game = _get_game(id)
    try:
        return game.get_driver_state(id)
    except ValueError as  e:
        raise HTTPException(status_code=404, detail=str(e))