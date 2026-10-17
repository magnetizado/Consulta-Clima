"""Aplicação FastAPI, cliente OpenWeatherMap e arquivos estáticos do dashboard."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.current import router as current_router
from app.clients.openweather import OpenWeatherClient, ProviderError

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
PROVIDER_ERROR_STATUS = {
    "provider_unauthorized": 502,
    "provider_rate_limited": 503,
    "provider_timeout": 504,
    "network_unavailable": 503,
    "provider_unavailable": 502,
}


def create_app(client: OpenWeatherClient | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if client is not None:
            app.state.client = client
            yield
            return

        api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
        if not api_key or api_key == "sua_chave_aqui":
            raise RuntimeError(
                "Configure OPENWEATHER_API_KEY no arquivo .env antes de iniciar o servidor."
            )

        async with httpx.AsyncClient() as http:
            app.state.client = OpenWeatherClient(http, api_key)
            yield

    app = FastAPI(title="Consulta Clima", lifespan=lifespan)
    app.include_router(current_router)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.exception_handler(ProviderError)
    async def provider_error_handler(request: Request, error: ProviderError) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=PROVIDER_ERROR_STATUS[error.code],
            content={"error": {"code": error.code}},
        )

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    return app


app = create_app()
