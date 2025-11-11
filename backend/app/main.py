# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.api.v1.routes import auth, materials, learning, health
from app.core.logging import configure_logging

def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="open_learning_assistant",
        version="0.1.0",
    )

    # CORS (adjust for your FE origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(materials.router, prefix="/api/v1/materials", tags=["materials"])
    app.include_router(learning.router, prefix="/api/v1/learning", tags=["learning"])

    return app


app = create_app()
