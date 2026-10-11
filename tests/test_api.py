import pytest
from httpx import AsyncClient, ASGITransport
from src.api.server import app
from src.database.session import init_db

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.anyio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "The Lenny Growth Assistant"

@pytest.mark.anyio
async def test_models_toggle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Get models
        get_res = await ac.get("/api/models")
        assert get_res.status_code == 200
        assert "ollama" in get_res.json()["available_providers"]

        # Switch to Anthropic
        post_res = await ac.post("/api/models", json={"provider": "anthropic"})
        assert post_res.status_code == 200
        assert post_res.json()["provider"] == "anthropic"

        # Switch back to Ollama
        reset_res = await ac.post("/api/models", json={"provider": "ollama"})
        assert reset_res.status_code == 200
        assert reset_res.json()["provider"] == "ollama"

@pytest.mark.anyio
async def test_session_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create session
        create_res = await ac.post("/api/sessions", json={"title": "Test Session"})
        assert create_res.status_code == 200
        sess_data = create_res.json()
        session_id = sess_data["id"]
        assert sess_data["title"] == "Test Session"

        # List sessions
        list_res = await ac.get("/api/sessions")
        assert list_res.status_code == 200
        assert any(s["id"] == session_id for s in list_res.json())

        # Get session detail
        detail_res = await ac.get(f"/api/sessions/{session_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["session"]["id"] == session_id

        # Delete session
        del_res = await ac.delete(f"/api/sessions/{session_id}")
        assert del_res.status_code == 200
