import pytest
import sys
import os
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

client = TestClient(app)

TEST_USER_EMAIL = f"student_{os.getpid()}@apextech.edu"
TEST_USER_PASSWORD = "StrongPassword2026!"
TEST_USER_NAME = "Sarah Connor"

def test_1_new_student_registration():
    """Test registering a brand new student user."""
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": TEST_USER_NAME,
        "college_name": "MIT College of Engineering",
        "degree": "B.Tech",
        "branch": "Computer Science & Engineering"
    }
    response = client.post("/auth/register", json=payload)
    # Could be 201 Created or 400 if rerun; if 400, test duplicate handling
    if response.status_code == 400:
        # Re-register with unique email
        payload["email"] = f"sarah_{os.getpid()}@apextech.edu"
        response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["full_name"] == TEST_USER_NAME

def test_2_duplicate_email_registration():
    """Test that registering an existing email returns 400 Bad Request."""
    payload = {
        "email": TEST_USER_EMAIL,
        "password": "AnotherPassword123!",
        "full_name": "Duplicate User"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"]

def test_3_login_valid_credentials():
    """Test login with correct email and password."""
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == TEST_USER_EMAIL
    assert len(data["access_token"]) > 20

def test_4_login_invalid_credentials():
    """Test login with incorrect password returns 401."""
    payload = {
        "email": TEST_USER_EMAIL,
        "password": "TotallyWrongPassword999!"
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

    # Non-existent email
    payload2 = {
        "email": "nonexistent.student.999@univ.edu",
        "password": "SomePassword123!"
    }
    response2 = client.post("/auth/login", json=payload2)
    assert response2.status_code == 401

def test_5_access_protected_profile_without_token():
    """Test GET /profile/me without token returns 401 Unauthorized."""
    response = client.get("/profile/me")
    assert response.status_code == 401
    assert "Authentication token required" in response.json()["detail"]

def test_6_access_protected_profile_with_invalid_token():
    """Test GET /profile/me with bogus token returns 401."""
    headers = {"Authorization": "Bearer bogus_invalid_token_12345"}
    response = client.get("/profile/me", headers=headers)
    assert response.status_code == 401

def test_7_get_current_student_profile():
    """Test GET /profile/me with valid JWT token."""
    login_res = client.post("/auth/login", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/profile/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER_EMAIL
    assert data["full_name"] == TEST_USER_NAME
    assert "technical_skills" in data
    assert "soft_skills" in data
    assert "programming_languages" in data

def test_8_update_student_profile():
    """Test PUT /profile/me updates student profile with comprehensive data."""
    login_res = client.post("/auth/login", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "full_name": "Sarah Connor - Updated",
        "college_name": "Apex Institute of Science & Tech",
        "degree": "B.Tech",
        "branch": "Computer Science & Artificial Intelligence",
        "cgpa": 8.92,
        "college_tier": "Tier 1",
        "current_year": 4,
        "current_semester": 7,
        "graduation_year": 2026,
        "roll_number": f"ROLL_{os.getpid()}",
        "phone": "+91 98765 43210",
        "technical_skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Machine Learning"],
        "soft_skills": ["Leadership", "Agile Collaboration", "Technical Writing", "Problem Solving"],
        "programming_languages": ["Python", "TypeScript", "C++", "SQL"],
        "coding_score": 88.5,
        "aptitude_score": 84.0,
        "communication_score": 90.0,
        "projects": [
            {
                "title": "AI Digital Career Twin",
                "tech_stack": ["React", "FastAPI", "PostgreSQL", "Scikit-learn"],
                "description": "Virtual career avatar modeling student placement readiness and simulation."
            }
        ],
        "certifications": [
            {
                "title": "AWS Certified Cloud Practitioner",
                "issuer": "Amazon Web Services",
                "year": 2025
            }
        ],
        "internships": [
            {
                "company": "TechCorp Innovations",
                "role": "Software Engineering Intern",
                "duration_months": 3
            }
        ],
        "interests": ["Artificial Intelligence", "Cloud Architecture", "Distributed Systems"],
        "career_goal": "Lead Architect at a global AI product engineering company",
        "target_company": "Google",
        "target_job_role": "Software Development Engineer"
    }

    response = client.put("/profile/me", json=update_payload, headers=headers)
    assert response.status_code == 200
    updated_data = response.json()

    assert updated_data["full_name"] == "Sarah Connor - Updated"
    assert updated_data["cgpa"] == 8.92
    assert updated_data["branch"] == "Computer Science & Artificial Intelligence"
    assert "FastAPI" in updated_data["technical_skills"]
    assert "TypeScript" in updated_data["programming_languages"]
    assert updated_data["coding_score"] == 88.5
    assert updated_data["target_company"] == "Google"
    assert len(updated_data["projects"]) == 1
    assert updated_data["projects"][0]["title"] == "AI Digital Career Twin"

def test_9_verify_persistence_on_refetch():
    """Verify that after PUT, subsequent GET reflects all updated values."""
    login_res = client.post("/auth/login", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/profile/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Sarah Connor - Updated"
    assert data["cgpa"] == 8.92
    assert data["target_job_role"] == "Software Development Engineer"

def test_10_logout_endpoint():
    """Test POST /auth/logout with token returns success message."""
    login_res = client.post("/auth/login", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]
