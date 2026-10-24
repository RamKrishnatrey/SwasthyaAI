# SwasthyaAI Health Endpoint Tests

import pytest
from httpx import AsyncClient
from app.main import create_app


@pytest.fixture
async def client():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "swasthyaai-backend"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_response_model(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # Validate required fields exist and have correct types
    assert isinstance(data["status"], str)
    assert isinstance(data["service"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["timestamp"], str)