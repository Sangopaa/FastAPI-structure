"""
Unit tests for StandardResponseRoute.

Tests that the route handler:
  - Wraps plain JSON responses in {ok, data, message}.
  - Does NOT double-wrap responses that already have the envelope format.
  - Correctly sets `ok=True` for 2xx and `ok=False` for 4xx/5xx.
  - Preserves a custom `message` field from the original payload.
"""

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from httpx import AsyncClient, ASGITransport

from core.standard_response_route import StandardResponseRoute


# ---------------------------------------------------------------------------
# Minimal test app that uses StandardResponseRoute
# ---------------------------------------------------------------------------


def make_app() -> FastAPI:
    test_app = FastAPI()
    test_app.router.route_class = StandardResponseRoute

    @test_app.get("/plain")
    def plain_response():
        return {"value": 42}

    @test_app.get("/with-message")
    def with_message():
        return {"value": 42, "message": "Custom message"}

    @test_app.get("/already-wrapped")
    def already_wrapped():
        return {"ok": True, "data": {"x": 1}, "message": "Already good"}

    @test_app.get("/error", status_code=400)
    def error_response():
        return JSONResponse(
            status_code=400,
            content={"detail": "bad request"},
        )

    return test_app


@pytest.fixture(name="test_client")
async def test_client_fixture():
    app = make_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_plain_response_is_wrapped(test_client: AsyncClient):
    """A plain dict response should be wrapped in the standard envelope."""
    response = await test_client.get("/plain")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"] == {"value": 42}
    assert body["message"] == "Success"


async def test_custom_message_is_preserved(test_client: AsyncClient):
    """A `message` key in the original payload should be hoisted to the envelope."""
    response = await test_client.get("/with-message")
    body = response.json()
    assert body["message"] == "Custom message"
    # `message` should NOT appear inside data after being hoisted
    assert "message" not in body["data"]


async def test_already_wrapped_is_not_double_wrapped(test_client: AsyncClient):
    """Responses that already contain the envelope must be returned as-is."""
    response = await test_client.get("/already-wrapped")
    body = response.json()
    # If double-wrapped, `body["data"]` would itself contain {ok, data, message}
    assert body["ok"] is True
    assert body["data"] == {"x": 1}
    assert body["message"] == "Already good"


async def test_error_response_has_ok_false(test_client: AsyncClient):
    """Non-2xx responses must have ok=False in the envelope."""
    response = await test_client.get("/error")
    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
