from httpx import ASGITransport, AsyncClient

from app.main import create_app


class StubChecker:
    def __init__(self, dependencies: dict[str, bool]) -> None:
        self.dependencies = dependencies

    async def check(self) -> dict[str, bool]:
        return self.dependencies


def client(dependencies: dict[str, bool]) -> AsyncClient:
    app = create_app(dependency_checker=StubChecker(dependencies))
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_health_is_live_and_sets_a_request_id() -> None:
    async with client({"database": True, "redis": True}) as api:
        response = await api.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


async def test_ready_reports_healthy_dependencies() -> None:
    async with client({"database": True, "redis": True}) as api:
        response = await api.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "dependencies": {"database": True, "redis": True}}


async def test_ready_safely_reports_unavailable_dependencies() -> None:
    async with client({"database": False, "redis": True}) as api:
        response = await api.get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "dependencies": {"database": False, "redis": True},
    }


async def test_local_frontend_origin_is_allowed() -> None:
    async with client({"database": True, "redis": True}) as api:
        response = await api.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
