"""Integration tests for the /documents API endpoints."""
import pytest
import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create a test client with an in-memory SQLite DB."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "server"))

    with patch("config.Settings.ensure_dirs"), \
         patch("ocr.registry.init_default_engines"), \
         patch("db.session.init_db"):
        from main import app
        from db.session import init_db
        init_db("sqlite:///./test_ocr.db")
        with TestClient(app) as c:
            yield c


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_upload_unsupported_type(client):
    data = io.BytesIO(b"not a real file")
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.docx", data, "application/msword")},
    )
    assert resp.status_code == 400


def test_get_nonexistent_document(client):
    resp = client.get("/api/v1/documents/nonexistent-id")
    assert resp.status_code == 404
