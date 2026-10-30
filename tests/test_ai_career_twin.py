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
from app.services.vector_store import vector_store

client = TestClient(app)

TEST_USER_EMAIL = f"twin_student_{os.getpid()}@apextech.edu"
TEST_USER_PASSWORD = "SecurePassword2026!"
TEST_USER_NAME = "Maya Lin"


@pytest.fixture(scope="module")
def auth_context():
    """Register and set up a student profile for AI Intelligence & Twin testing."""
    reg_payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": TEST_USER_NAME,
        "college_name": "International Tech University",
        "degree": "B.Tech",
        "branch": "Computer Science & Engineering"
    }
    res = client.post("/auth/register", json=reg_payload)
    if res.status_code == 201:
        token = res.json()["access_token"]
        user_id = res.json()["user"]["id"]
    else:
        login_res = client.post("/auth/login", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
        token = login_res.json()["access_token"]
        user_id = login_res.json()["user"]["id"]

    headers = {"Authorization": f"Bearer {token}"}

    # Populate student profile with rich data
    profile_payload = {
        "full_name": TEST_USER_NAME,
        "phone": "+91 9988776655",
        "cgpa": 8.75,
        "technical_skills": ["Python", "SQL", "FastAPI", "React", "Git"],
        "programming_languages": ["Python", "JavaScript"],
        "soft_skills": ["Problem Solving", "Collaboration", "Public Speaking"],
        "interests": ["Backend Systems", "Machine Learning"],
        "projects": [
            {
                "title": "Real-time Telemetry Dashboard",
                "description": "FastAPI + WebSockets event engine.",
                "tech_stack": ["Python", "FastAPI", "Redis"]
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Cloud Practitioner",
                "issuer": "AWS",
                "year": 2025
            }
        ],
        "internships": [
            {
                "company": "CloudScale Systems",
                "role": "Backend Intern",
                "duration_months": 3
            }
        ],
        "coding_score": 82.0,
        "aptitude_score": 80.0,
        "communication_score": 85.0,
        "mock_interview_score": 80.0,
        "backlogs": 0
    }
    client.put("/profile/me", headers=headers, json=profile_payload)

    # Select target job
    jobs_res = client.get("/jobs", headers=headers)
    if jobs_res.status_code == 200 and len(jobs_res.json()) > 0:
        first_job = jobs_res.json()[0]
        client.post(f"/jobs/{first_job['id']}/select-target", headers=headers)
        client.post(f"/skill-gap/analyze/{first_job['id']}", headers=headers)
        client.post("/placement/predict", headers=headers)
        client.post("/roadmap/generate", headers=headers)

    return {"headers": headers, "email": TEST_USER_EMAIL, "user_id": user_id}


# ============================================================================
# 1. MODULE 1 — CAREER KNOWLEDGE BASE & VECTOR STORE TESTS
# ============================================================================

def test_1_knowledge_base_indexing():
    """Verify that career knowledge base documents are chunked and indexed in FAISS."""
    assert vector_store.index is not None
    assert vector_store.index.ntotal > 0
    assert len(vector_store.chunks) > 0


def test_2_embedding_generation_and_retrieval():
    """Verify that dense embeddings generate accurate semantic vector search results."""
    query = "What skills should I learn for Machine Learning Engineer?"
    results = vector_store.search(query=query, top_k=3)
    assert len(results) > 0
    assert any("Machine Learning" in r["title"] or "Python" in r["title"] for r in results)
    for r in results:
        assert 0.0 <= r["similarity_score"] <= 1.0
        assert "content" in r
        assert "category" in r


# ============================================================================
# 2. MODULE 2 — RAG CAREER ASSISTANT TESTS
# ============================================================================

def test_3_rag_career_assistant_response(auth_context):
    """Test RAG assistant endpoint with question answering, telemetry context, and citations."""
    payload = {
        "question": "What skills am I missing for my target role, and what should I build next?"
    }
    res = client.post("/ai/career-assistant", headers=auth_context["headers"], json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "answer" in data
    assert len(data["answer"]) > 50
    assert "retrieved_sources" in data
    assert len(data["retrieved_sources"]) > 0
    assert "student_context" in data
    assert data["student_context"]["student_name"] == TEST_USER_NAME
    assert "suggested_followups" in data
    assert len(data["suggested_followups"]) > 0


def test_4_rag_career_assistant_validation(auth_context):
    """Test validation when question is empty."""
    res = client.post("/ai/career-assistant", headers=auth_context["headers"], json={"question": "   "})
    assert res.status_code == 400


# ============================================================================
# 3. MODULE 3 — LLM PERSONALIZED RECOMMENDATIONS TESTS
# ============================================================================

def test_5_llm_personalized_recommendations(auth_context):
    """Test LLM personalized recommendations without altering deterministic scores."""
    res = client.get("/ai/recommendations", headers=auth_context["headers"])
    assert res.status_code == 200
    data = res.json()

    assert "target_role" in data
    assert "target_company" in data
    assert "deterministic_skill_match" in data
    assert "deterministic_placement_score" in data
    assert "next_skill_to_learn" in data
    assert "recommended_project" in data
    assert "learning_priorities" in data
    assert "interview_preparation" in data
    assert "improvement_suggestions" in data
    assert len(data["learning_priorities"]) > 0


# ============================================================================
# 4. MODULE 4 & 5 — DIGITAL CAREER TWIN & UPDATE ENGINE TESTS
# ============================================================================

def test_6_get_digital_career_twin_state(auth_context):
    """Test retrieving and initializing the Digital Career Twin."""
    res = client.get("/twin/state", headers=auth_context["headers"])
    assert res.status_code == 200
    twin_data = res.json()

    assert twin_data["twin_name"] is not None
    assert twin_data["overall_twin_score"] > 0
    assert 0 <= twin_data["benchmark_percentile"] <= 100
    assert "radar_breakdown" in twin_data
    assert "Coding" in twin_data["radar_breakdown"]
    assert "Aptitude" in twin_data["radar_breakdown"]
    assert "Projects" in twin_data["radar_breakdown"]

    # Verify persistence in database
    db = SessionLocal()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == auth_context["user_id"]).first()
    twin_record = db.query(DigitalCareerTwin).filter(
        DigitalCareerTwin.student_profile_id == profile.id
    ).first()
    db.close()
    assert twin_record is not None
    assert twin_record.overall_twin_score == twin_data["overall_twin_score"]


def test_7_sync_digital_career_twin(auth_context):
    """Test explicit synchronization of the Career Twin."""
    res = client.post("/twin/sync?event_label=TestSyncEvent", headers=auth_context["headers"])
    assert res.status_code == 200
    synced_data = res.json()
    assert synced_data["overall_twin_score"] > 0
    assert synced_data["twin_version"] >= 1


def test_8_automatic_twin_update_on_profile_change(auth_context):
    """Test that updating profile skills automatically triggers Career Twin recalculation."""
    initial_res = client.get("/twin/state", headers=auth_context["headers"])
    initial_score = initial_res.json()["coding_score"]

    # Update coding score on profile
    client.put("/profile/me", headers=auth_context["headers"], json={
        "coding_score": 92.0
    })

    # Fetch updated twin
    updated_res = client.get("/twin/state", headers=auth_context["headers"])
    updated_data = updated_res.json()
    assert updated_data["coding_score"] == 92.0
    assert updated_data["coding_score"] != initial_score


# ============================================================================
# 5. MODULE 6 — WHAT-IF CAREER SIMULATION TESTS
# ============================================================================

def test_9_what_if_career_simulation(auth_context):
    """Test What-If simulation non-destructively predicts career gains."""
    sim_payload = {
        "added_skills": ["AWS", "Docker", "Kubernetes"],
        "added_projects_count": 1,
        "coding_score_delta": 10.0,
        "aptitude_score_delta": 5.0,
        "added_internships_count": 0
    }
    res = client.post("/twin/simulate", headers=auth_context["headers"], json=sim_payload)
    assert res.status_code == 200
    sim_data = res.json()

    assert sim_data["is_simulation"] is True
    assert "disclaimer" in sim_data
    assert "baseline" in sim_data
    assert "simulated" in sim_data
    assert "deltas" in sim_data

    # Verify projected improvement
    assert sim_data["deltas"]["placement_readiness_delta"] >= 0
    assert sim_data["deltas"]["match_percentage_delta"] >= 0
    assert len(sim_data["resolved_skills"]) > 0

    # Ensure actual profile is completely untouched
    db = SessionLocal()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == auth_context["user_id"]).first()
    db.close()
    assert "Kubernetes" not in (profile.technical_skills or [])


# ============================================================================
# 6. SECURITY, AUTHENTICATION & ACCESS CONTROL TESTS
# ============================================================================

def test_10_ai_endpoints_unauthenticated_blocked():
    """Verify that unauthenticated requests to AI & Twin endpoints are rejected with 401."""
    endpoints = [
        ("POST", "/ai/career-assistant", {"question": "Test"}),
        ("GET", "/ai/recommendations", None),
        ("GET", "/twin/state", None),
        ("POST", "/twin/sync", None),
        ("POST", "/twin/simulate", {"added_skills": []})
    ]
    for method, path, body in endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json=body or {})
        assert res.status_code in [401, 403], f"Expected 401/403 for {method} {path}, got {res.status_code}"


# ============================================================================
# 7. REGRESSION VERIFICATION — PHASE 3 FUNCTIONALITY REMAINS INTACT
# ============================================================================

def test_11_phase_3_career_modules_still_functional(auth_context):
    """Verify company, job, skill gap, placement, and roadmap continue functioning seamlessly."""
    # 1. Company listing
    c_res = client.get("/companies", headers=auth_context["headers"])
    assert c_res.status_code == 200 and len(c_res.json()) >= 10

    # 2. Target job
    j_res = client.get("/jobs/my-target", headers=auth_context["headers"])
    assert j_res.status_code == 200

    # 3. Skill gap latest
    sg_res = client.get("/skill-gap/latest", headers=auth_context["headers"])
    assert sg_res.status_code == 200

    # 4. Placement latest
    pl_res = client.get("/placement/latest", headers=auth_context["headers"])
    assert pl_res.status_code == 200

    # 5. Roadmap
    rm_res = client.get("/roadmap", headers=auth_context["headers"])
    assert rm_res.status_code == 200 and len(rm_res.json()["stages"]) == 7
