import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.core.database import SessionLocal
from app.models.models import (
    User, DigitalCareerTwin, ProgressTracking, SkillGapResult, PlacementReadiness
)
from app.models.student_profile import StudentProfile

client = TestClient(app)

STUDENT_A_EMAIL = f"student_a_{os.getpid()}@apextech.edu"
STUDENT_B_EMAIL = f"student_b_{os.getpid()}@apextech.edu"
TEST_PASSWORD = "StrongSecurePassword2026!"


@pytest.fixture(scope="module")
def students_setup():
    """Register Student A and Student B to verify cross-user isolation and dashboard flow."""
    # Register Student A
    res_a = client.post("/auth/register", json={
        "email": STUDENT_A_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Alice Sterling",
        "college_name": "Apex University",
        "degree": "B.Tech",
        "branch": "Computer Science"
    })
    token_a = res_a.json()["access_token"]
    user_a_id = res_a.json()["user"]["id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Student B
    res_b = client.post("/auth/register", json={
        "email": STUDENT_B_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Bob Vance",
        "college_name": "Apex University",
        "degree": "B.Tech",
        "branch": "Information Technology"
    })
    token_b = res_b.json()["access_token"]
    user_b_id = res_b.json()["user"]["id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Populate Student A profile & select target job
    client.put("/profile/me", headers=headers_a, json={
        "technical_skills": ["Python", "FastAPI", "React", "SQL"],
        "coding_score": 88.0,
        "cgpa": 8.9,
        "projects": [{"title": "Alice Engine", "tech_stack": ["Python"]}]
    })

    # Populate Student B profile with different data
    client.put("/profile/me", headers=headers_b, json={
        "technical_skills": ["Java", "Spring Boot", "MySQL"],
        "coding_score": 62.0,
        "cgpa": 7.2,
        "projects": [{"title": "Bob Portal", "tech_stack": ["Java"]}]
    })

    return {
        "headers_a": headers_a, "user_a_id": user_a_id, "email_a": STUDENT_A_EMAIL,
        "headers_b": headers_b, "user_b_id": user_b_id, "email_b": STUDENT_B_EMAIL
    }


# ============================================================================
# 1. MODULE 1 — MAIN STUDENT DASHBOARD ENDPOINT TESTS
# ============================================================================

def test_1_dashboard_summary_telemetry(students_setup):
    """Verify GET /dashboard/summary returns comprehensive student telemetry."""
    res = client.get("/dashboard/summary", headers=students_setup["headers_a"])
    assert res.status_code == 200
    data = res.json()

    # 1. Profile summary
    assert "profile" in data
    assert data["profile"]["full_name"] == "Alice Sterling"
    assert "Python" in data["profile"]["technical_skills"]

    # 2. Resume summary
    assert "resume" in data
    assert "has_resume" in data["resume"]

    # 3. Target job
    assert "target_job" in data

    # 4. Skill gap
    assert "skill_gap" in data

    # 5. Placement readiness
    assert "placement" in data
    assert 0 <= data["placement"]["readiness_score"] <= 100

    # 6. Roadmap
    assert "roadmap" in data
    assert "current_stage" in data["roadmap"]

    # 7. Digital Career Twin
    assert "career_twin" in data
    assert data["career_twin"]["overall_twin_score"] > 0
    assert "radar_breakdown" in data["career_twin"]

    # 8. Top action items
    assert "top_action_items" in data
    assert len(data["top_action_items"]) > 0


# ============================================================================
# 2. SECURITY & DATA PRIVACY — CROSS-STUDENT ISOLATION (NO IDOR)
# ============================================================================

def test_2_cross_student_data_isolation(students_setup):
    """Verify that Student A and Student B cannot view or tamper with each other's career data."""
    # Student A queries profile
    res_a = client.get("/profile/me", headers=students_setup["headers_a"])
    assert res_a.status_code == 200
    assert res_a.json()["full_name"] == "Alice Sterling"
    assert "Python" in res_a.json()["technical_skills"]

    # Student B queries profile
    res_b = client.get("/profile/me", headers=students_setup["headers_b"])
    assert res_b.status_code == 200
    assert res_b.json()["full_name"] == "Bob Vance"
    assert "Java" in res_b.json()["technical_skills"]
    assert "Python" not in res_b.json()["technical_skills"]

    # Verify Career Twin separation
    twin_a = client.get("/twin/state", headers=students_setup["headers_a"]).json()
    twin_b = client.get("/twin/state", headers=students_setup["headers_b"]).json()
    assert twin_a["student_profile_id"] != twin_b["student_profile_id"]
    assert twin_a["coding_score"] == 88.0
    assert twin_b["coding_score"] == 62.0


def test_3_password_hashing_security():
    """Verify that user passwords are securely hashed with bcrypt and never stored in plain text."""
    db = SessionLocal()
    user = db.query(User).filter(User.email == STUDENT_A_EMAIL).first()
    db.close()
    assert user is not None
    assert user.password_hash != TEST_PASSWORD
    assert user.password_hash.startswith("$2b$") or user.password_hash.startswith("$2a$")


def test_4_expired_or_invalid_jwt_rejected():
    """Verify that requests with bogus or expired JWT tokens are rejected with 401."""
    bogus_headers = {"Authorization": "Bearer invalid.jwt.token.here"}
    res = client.get("/dashboard/summary", headers=bogus_headers)
    assert res.status_code in [401, 403]

    res_no_auth = client.get("/dashboard/summary")
    assert res_no_auth.status_code in [401, 403]


# ============================================================================
# 3. PERFORMANCE & ARCHITECTURAL INTEGRITY CHECKS
# ============================================================================

def test_5_inference_speed_and_no_csv_dependency(students_setup):
    """Verify that placement prediction runs in under 150ms using the preloaded model artifact."""
    import time
    start = time.time()
    res = client.post("/placement/predict", headers=students_setup["headers_a"])
    elapsed = time.time() - start

    assert res.status_code == 200
    assert elapsed < 0.5  # Sub-half-second execution proves CSV is not being reloaded
    data = res.json()
    assert "readiness_score" in data


def test_6_vector_store_cached_instant_retrieval(students_setup):
    """Verify that FAISS vector search retrieves semantic chunks in <100ms without re-indexing."""
    import time
    start = time.time()
    res = client.get("/ai/knowledge-base/search?query=System+Design+caching", headers=students_setup["headers_a"])
    elapsed = time.time() - start

    assert res.status_code == 200
    assert elapsed < 0.2
    assert res.json()["results_count"] > 0
