"""FastAPI application factory for EduKnowledge AI."""

import logging
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.api.v1.programs import router as programs_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.db.session import DependencyChecker, InfrastructureChecker, build_infrastructure

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    checker = app.state.dependency_checker
    if isinstance(checker, InfrastructureChecker):
        await checker.close()


def create_app(
    settings: Settings | None = None, dependency_checker: DependencyChecker | None = None
) -> FastAPI:
    """Create an independently configurable application instance for HTTP and tests."""
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    app = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        description="Demo-only, source-grounded educational knowledge assistant.",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    checker = dependency_checker or build_infrastructure(resolved_settings)
    app.state.dependency_checker = checker
    app.state.session_factory = (
        checker.session_factory if isinstance(checker, InfrastructureChecker) else None
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled request error", extra={"request_id": request_id})
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_complete",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
            },
        )
        return response

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(programs_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    return app


app = create_app()
