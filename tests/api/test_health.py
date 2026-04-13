"""
Integration tests for the /health endpoint.
"""

from httpx import AsyncClient


async def test_health_returns_200(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200


async def test_health_response_body(client: AsyncClient):
    response = await client.get("/health")
    data = response.json()
    assert data == {"status": "running"}
