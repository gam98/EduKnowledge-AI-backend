"""Unauthenticated liveness and dependency-readiness endpoints."""

from typing import Literal

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel

from app.db.session import DependencyChecker

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    dependencies: dict[str, bool]


def get_dependency_checker(request: Request) -> DependencyChecker:
    return request.app.state.dependency_checker


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Confirm the process can serve HTTP without checking external dependencies."""
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Dependency unavailable"}},
)
async def ready(request: Request, response: Response) -> ReadinessResponse:
    """Report only boolean dependency status, keeping operational details private."""
    dependencies = await get_dependency_checker(request).check()
    is_ready = all(dependencies.values())
    payload = ReadinessResponse(
        status="ready" if is_ready else "not_ready", dependencies=dependencies
    )
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload
