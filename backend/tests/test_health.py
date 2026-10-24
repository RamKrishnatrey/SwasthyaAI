import asyncio

import httpx

from backend.swasthyaai.config import get_settings
from backend.swasthyaai.db import init_db
from backend.swasthyaai.main import create_app


def test_health_reports_demo_mode():
    async def get_health():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=create_app()),
            base_url="http://test",
        ) as client:
            return await client.get("/api/v1/health")

    response = asyncio.run(get_health())

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "demo"}


def test_settings_use_configured_data_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("SWASTHYAAI_DATA_DIR", str(tmp_path))

    assert get_settings().data_dir == tmp_path


def test_database_is_created_inside_configured_directory(tmp_path):
    database = tmp_path / "nested" / "swasthya.sqlite3"

    init_db(database)

    assert database.is_file()
