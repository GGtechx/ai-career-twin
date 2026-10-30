import pytest
import sys
import os
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root API endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data

def test_health_check_endpoint():
    """Test /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["app_name"] == "AI Digital Career Twin"
    assert data["database_status"] == "connected"
    assert data["tables_registered_count"] == 21
    assert data["tables_created_in_db_count"] == 21

def test_health_db_details_endpoint():
    """Test /api/health/db endpoint."""
    response = client.get("/api/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert data["total_tables"] == 21
    assert "users" in data["table_names"]
    assert "student_profiles" in data["table_names"]
    assert "digital_career_twin" in data["table_names"]
    assert "placement_readiness" in data["table_names"]
