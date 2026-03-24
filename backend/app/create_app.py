from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.state.game_state import GameState
from backend.api.routes import router

def create_app() -> FastAPI:
    app = FastAPI(
        title='Rallyman GT',
        version='0.1.0',
        description='Rallyman GT race stats app'
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
    app.state.game_state = GameState()
    app.include_router(router, prefix='/api')
    return app