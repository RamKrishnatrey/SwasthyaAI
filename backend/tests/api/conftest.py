import asyncio

import httpx
import pytest

from backend.swasthyaai.main import create_app


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("SWASTHYAAI_DATA_DIR", str(tmp_path))
    return create_app()


def call(app, method, path, **kwargs):
    async def request():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(request())


def register_and_login(app, role="patient", email="person@example.test"):
    created = call(app, "POST", "/api/v1/auth/register", json={
        "email": email, "password": "correct horse battery staple", "role": role
    })
    assert created.status_code == 201
    logged_in = call(app, "POST", "/api/v1/auth/login", json={
        "email": email, "password": "correct horse battery staple"
    })
    assert logged_in.status_code == 200
    return logged_in.json()["access_token"]
