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
    User, Company, JobRole, JobRequirement, SkillGapResult,
    PlacementReadiness, Recommendation, CareerRoadmap, ProgressTracking
)
from app.models.student_profile import StudentProfile

client = TestClient(app)

TEST_USER_EMAIL = f"career_student_{os.getpid()}@apextech.edu"
TEST_USER_PASSWORD = "SecurePassword2026!"
TEST_USER_NAME = "Elena Rostova"


@pytest.fixture(scope="module")
def auth_context():
    """Register and set up a student profile for Career Analysis testing."""
    reg_payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": TEST_USER_NAME,
        "college_name": "National Tech University",
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

    # Populate profile with rich data for realistic ML & gap analysis
    profile_payload = {
        "full_name": TEST_USER_NAME,
        "phone": "+91 9123456780",
        "cgpa": 8.65,
        "technical_skills": ["Python", "SQL", "Git", "FastAPI", "React", "Docker"],
        "programming_languages": ["Python", "JavaScript"],
        "soft_skills": ["Problem Solving", "Communication", "Teamwork"],
        "interests": ["Machine Learning", "Backend Engineering"],
        "projects": [
            {
                "title": "Smart Career Recommendation Engine",
                "description": "Built using FastAPI and Scikit-Learn with TF-IDF similarity.",
                "tech_stack": ["Python", "FastAPI", "Docker"]
            },
            {
                "title": "Portfolio Web App",
                "description": "React interactive frontend with TailwindCSS.",
                "tech_stack": ["React", "JavaScript"]
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Cloud Practitioner",
                "issuer": "Amazon Web Services",
                "year": 2025
            }
        ],
        "internships": [
            {
                "company": "NextGen Labs",
                "role": "Software Engineering Intern",
                "duration_months": 4
            }
        ],
        "coding_score": 85.0,
        "aptitude_score": 82.0,
        "communication_score": 80.0,
        "mock_interview_score": 84.0,
        "backlogs": 0
    }
    client.put("/profile/me", headers=headers, json=profile_payload)

    return {"headers": headers, "email": TEST_USER_EMAIL, "user_id": user_id}


# ============================================================================
# 1. MODULE 1 — COMPANY & JOB REQUIREMENTS TESTS
# ============================================================================

def test_1_list_companies(auth_context):
    """Test retrieving list of companies with seeding and search capabilities."""
    res = client.get("/companies", headers=auth_context["headers"])
    assert res.status_code == 200
    companies = res.json()
    assert len(companies) >= 10
    assert any(c["name"] == "Google" for c in companies)
    assert any(c["name"] == "Microsoft" for c in companies)

    # Test search filter
    search_res = client.get("/companies?search=Google", headers=auth_context["headers"])
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data) >= 1
    assert "Google" in search_data[0]["name"]


def test_2_get_company_details(auth_context):
    """Test retrieving individual company by ID."""
    res = client.get("/companies", headers=auth_context["headers"])
    first_company = res.json()[0]
    company_id = first_company["id"]

    detail_res = client.get(f"/companies/{company_id}", headers=auth_context["headers"])
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["id"] == company_id
    assert data["name"] == first_company["name"]
    assert "active_jobs_count" in data


def test_3_list_and_filter_jobs(auth_context):
    """Test listing all job roles and filtering by company."""
    res = client.get("/jobs", headers=auth_context["headers"])
    assert res.status_code == 200
    jobs = res.json()
    assert len(jobs) >= 15

    first_job = jobs[0]
    company_id = first_job["company_id"]
    filtered_res = client.get(f"/jobs?company_id={company_id}", headers=auth_context["headers"])
    assert filtered_res.status_code == 200
    filtered_jobs = filtered_res.json()
    assert all(j["company_id"] == company_id for j in filtered_jobs)


def test_4_get_job_requirements(auth_context):
    """Test retrieving complete job requirements including eligibility & skill weights."""
    res = client.get("/jobs", headers=auth_context["headers"])
    first_job = res.json()[0]
    job_id = first_job["id"]

    req_res = client.get(f"/jobs/{job_id}/requirements", headers=auth_context["headers"])
    assert req_res.status_code == 200
    req_data = req_res.json()
    assert "must_have_skills" in req_data
    assert "good_to_have_skills" in req_data
    assert len(req_data["must_have_skills"]) > 0
    assert "min_cgpa" in req_data
    assert req_data["min_cgpa"] >= 6.0


def test_5_select_target_job(auth_context):
    """Test student selecting a target job and checking persistence."""
    res = client.get("/jobs", headers=auth_context["headers"])
    chosen_job = res.json()[0]
    job_id = chosen_job["id"]

    select_res = client.post(f"/jobs/{job_id}/select-target", headers=auth_context["headers"])
    assert select_res.status_code == 200
    sel_data = select_res.json()
    assert sel_data["target_job_role_id"] == job_id
    assert "target_job_title" in sel_data

    # Verify retrieval of current target job via /jobs/my-target
    target_res = client.get("/jobs/my-target", headers=auth_context["headers"])
    assert target_res.status_code == 200
    target_data = target_res.json()
    assert target_data is not None
    assert target_data["id"] == job_id


# ============================================================================
# 2. MODULE 2 — SKILL GAP ANALYSIS TESTS
# ============================================================================

def test_6_skill_gap_analysis(auth_context):
    """Test skill gap execution with NLP normalization and TF-IDF cosine matching."""
    res = client.get("/jobs", headers=auth_context["headers"])
    job_id = res.json()[0]["id"]

    gap_res = client.post(f"/skill-gap/analyze/{job_id}", headers=auth_context["headers"])
    assert gap_res.status_code == 200
    gap_data = gap_res.json()

    assert "match_percentage" in gap_data
    assert 0 <= gap_data["match_percentage"] <= 100
    assert "matched_skills" in gap_data
    assert "missing_critical_skills" in gap_data
    assert "missing_secondary_skills" in gap_data
    assert "priority_skill_gaps" in gap_data
    assert "recommended_skills" in gap_data
    assert isinstance(gap_data["priority_skill_gaps"], list)

    # Check persistence in database
    db = SessionLocal()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == auth_context["user_id"]).first()
    saved_gap = db.query(SkillGapResult).filter(
        SkillGapResult.student_profile_id == profile.id,
        SkillGapResult.job_role_id == job_id
    ).first()
    db.close()
    assert saved_gap is not None
    assert saved_gap.match_percentage == gap_data["match_percentage"]


def test_7_get_latest_skill_gap(auth_context):
    """Test retrieving most recent skill gap record."""
    latest_res = client.get("/skill-gap/latest", headers=auth_context["headers"])
    assert latest_res.status_code == 200
    data = latest_res.json()
    assert data is not None
    assert "match_percentage" in data


# ============================================================================
# 3. MODULE 3 — PLACEMENT READINESS PREDICTION TESTS
# ============================================================================

def test_8_placement_readiness_prediction(auth_context):
    """Test live ML placement readiness prediction using student DB attributes."""
    predict_res = client.post("/placement/predict", headers=auth_context["headers"])
    assert predict_res.status_code == 200
    pred = predict_res.json()

    assert "readiness_score" in pred
    assert 0 <= pred["readiness_score"] <= 100
    assert pred["readiness_category"] in ["Placement Ready (High)", "Moderate Readiness", "At Risk"]
    assert "strengths" in pred and len(pred["strengths"]) > 0
    assert "weak_areas" in pred
    assert "improvement_suggestions" in pred
    assert "feature_breakdown" in pred

    # Verify persistence in database
    db = SessionLocal()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == auth_context["user_id"]).first()
    saved_pred = db.query(PlacementReadiness).filter(
        PlacementReadiness.student_profile_id == profile.id
    ).order_by(PlacementReadiness.assessed_at.desc()).first()
    db.close()
    assert saved_pred is not None
    assert saved_pred.readiness_score == pred["readiness_score"]


def test_9_get_latest_placement_readiness(auth_context):
    """Test fetching latest placement readiness record."""
    latest_res = client.get("/placement/latest", headers=auth_context["headers"])
    assert latest_res.status_code == 200
    data = latest_res.json()
    assert data is not None
    assert "readiness_score" in data


# ============================================================================
# 4. MODULE 4 — PERSONALIZED CAREER RECOMMENDATIONS TESTS
# ============================================================================

def test_10_generate_and_list_recommendations(auth_context):
    """Test generating personalized recommendations across all 7 categories."""
    gen_res = client.post("/recommendations/generate", headers=auth_context["headers"])
    assert gen_res.status_code == 200
    rec_data = gen_res.json()

    assert "total_recommendations" in rec_data
    assert rec_data["total_recommendations"] > 0
    assert "by_category" in rec_data

    categories = set(rec_data["by_category"].keys())
    expected_categories = {"skill", "course", "project", "certification", "coding", "aptitude", "interview"}
    assert len(categories.intersection(expected_categories)) >= 4

    # Test listing recommendations
    list_res = client.get("/recommendations", headers=auth_context["headers"])
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total_recommendations"] == rec_data["total_recommendations"]


def test_11_recommendation_status_actions(auth_context):
    """Test completing and dismissing a recommendation."""
    list_res = client.get("/recommendations", headers=auth_context["headers"])
    data = list_res.json()
    by_cat = data.get("by_category", {})
    all_items = []
    for cat_items in by_cat.values():
        all_items.extend(cat_items)

    assert len(all_items) > 0
    first_id = all_items[0]["id"]

    # Mark as completed
    complete_res = client.patch(f"/recommendations/{first_id}/complete", headers=auth_context["headers"])
    assert complete_res.status_code == 200
    assert complete_res.json()["is_completed"] is True

    # Mark second as dismissed if available
    if len(all_items) > 1:
        second_id = all_items[1]["id"]
        dismiss_res = client.patch(f"/recommendations/{second_id}/dismiss", headers=auth_context["headers"])
        assert dismiss_res.status_code == 200
        assert dismiss_res.json()["is_dismissed"] is True


# ============================================================================
# 5. MODULE 5 — PERSONALIZED CAREER ROADMAP TESTS
# ============================================================================

def test_12_generate_and_fetch_roadmap(auth_context):
    """Test generating 7-stage roadmap and verifying structure."""
    gen_res = client.post("/roadmap/generate", headers=auth_context["headers"])
    assert gen_res.status_code == 200
    roadmap_data = gen_res.json()

    assert "stages" in roadmap_data
    stages = roadmap_data["stages"]
    assert len(stages) == 7

    stage_names = [s["stage_name"] for s in stages]
    assert "Skill Foundation" in stage_names
    assert "Skill Development" in stage_names
    assert "Project Development" in stage_names
    assert "Certification" in stage_names
    assert "Coding & Aptitude" in stage_names
    assert "Interview Preparation" in stage_names
    assert "Placement Ready" in stage_names

    # Test fetching roadmap via GET
    get_res = client.get("/roadmap", headers=auth_context["headers"])
    assert get_res.status_code == 200
    assert len(get_res.json()["stages"]) == 7


def test_13_update_roadmap_task_progress(auth_context):
    """Test marking roadmap tasks as complete and verifying progress tracking in DB."""
    get_res = client.get("/roadmap", headers=auth_context["headers"])
    roadmap_data = get_res.json()
    first_item = roadmap_data["stages"][0]["items"][0]
    task_id = first_item["item_id"]

    # Toggle task to completed
    update_res = client.patch(
        f"/roadmap/tasks/{task_id}",
        headers=auth_context["headers"],
        json={"status": "Completed", "completion_percentage": 100.0}
    )
    assert update_res.status_code == 200
    updated_roadmap = update_res.json()
    assert updated_roadmap["completed_tasks"] >= 1
    assert updated_roadmap["overall_progress_percentage"] > 0

    # Verify progress tracking logged in database
    db = SessionLocal()
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == auth_context["user_id"]).first()
    progress_entry = db.query(ProgressTracking).filter(
        ProgressTracking.student_profile_id == profile.id
    ).first()
    db.close()
    assert progress_entry is not None


# ============================================================================
# 6. AUTHENTICATION & SECURITY ENFORCEMENT
# ============================================================================

def test_14_unauthenticated_requests_blocked():
    """Verify that unauthenticated requests receive 401 Unauthorized."""
    endpoints = [
        ("GET", "/jobs/my-target"),
        ("POST", "/jobs/1/select-target"),
        ("POST", "/skill-gap/analyze/1"),
        ("GET", "/skill-gap/latest"),
        ("POST", "/placement/predict"),
        ("GET", "/placement/latest"),
        ("POST", "/recommendations/generate"),
        ("GET", "/recommendations"),
        ("GET", "/roadmap"),
        ("POST", "/roadmap/generate")
    ]
    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path)
        assert res.status_code in [401, 403], f"Expected 401/403 for unauthenticated {method} {path}, got {res.status_code}"
