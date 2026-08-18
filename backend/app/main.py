"""AI2Doc FastAPI application composition root."""

from __future__ import annotations

import asyncio
import contextlib
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.convert import router as convert_router
from app.api.files import router as files_router
from app.api.health import router as health_router
from app.config import Settings, get_settings
from app.errors import AI2DocError
from app.services.conversion import ConversionService
from app.services.files import TemporaryFileStore
from app.services.pandoc import PandocRunner


def create_app(
    settings: Settings | None = None,
    pandoc_runner: PandocRunner | None = None,
) -> FastAPI:
    """Build an application with replaceable infrastructure for testing."""

    app_settings = settings or get_settings()
    file_store = TemporaryFileStore(app_settings)
    runner = pandoc_runner or PandocRunner(app_settings)
    conversion_service = ConversionService(app_settings, file_store, runner)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        file_store.ensure_storage()
        file_store.cleanup_expired()

        async def cleanup_loop() -> None:
            while True:
                await asyncio.sleep(app_settings.cleanup_interval_seconds)
                file_store.cleanup_expired()

        cleanup_task = asyncio.create_task(cleanup_loop())
        try:
            yield
        finally:
            cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await cleanup_task

    app = FastAPI(
        title="AI2Doc API",
        version="0.1.0",
        description="Convert AI-authored Markdown into template-based DOCX files.",
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.state.file_store = file_store
    app.state.pandoc_runner = runner
    app.state.conversion_service = conversion_service

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(app_settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
        expose_headers=["Content-Disposition", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(AI2DocError)
    async def handle_ai2doc_error(request: Request, exc: AI2DocError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": getattr(request.state, "request_id", None),
                },
            },
        )

    app.include_router(health_router)
    app.include_router(convert_router)
    app.include_router(files_router)
    return app


app = create_app()
