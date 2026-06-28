from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.modules.auth.api import router as auth_router


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    configure_logging(active_settings)

    app = FastAPI(
        title=active_settings.project_name,
        version="0.1.0",
        docs_url="/docs" if active_settings.is_development else None,
        redoc_url="/redoc" if active_settings.is_development else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "api"}

    @app.get("/ready", tags=["system"])
    async def ready() -> dict[str, str]:
        return {"status": "ready", "service": "api"}

    @app.get("/api/v1/system/info", tags=["system"])
    async def system_info() -> dict[str, str]:
        return {
            "name": active_settings.project_name,
            "environment": active_settings.app_env,
            "version": "0.1.0",
        }

    app.include_router(auth_router)

    return app


app = create_app()
