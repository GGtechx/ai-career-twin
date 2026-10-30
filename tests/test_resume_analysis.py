import io
import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.core.database import SessionLocal
from app.models.models import Resume, User
from app.models.student_profile import StudentProfile
from app.utils.text_extraction import extract_text_from_pdf_bytes, clean_text
from app.services.resume_analyzer import (
    analyze_resume,
    extract_skills_from_text,
    extract_education,
    extract_projects,
    compare_with_profile,
    calculate_ats_score
)

client = TestClient(app)

TEST_USER_EMAIL = f"resume_student_{os.getpid()}@apextech.edu"
TEST_USER_PASSWORD = "StrongPassword2026!"
TEST_USER_NAME = "Alexander Wright"


def make_pdf_bytes(lines: list) -> bytes:
    """Helper to generate valid PDF 1.4 bytes in-memory for testing."""
    body = ""
    y = 720
    for line in lines:
        safe_line = line.replace("(", "\\(").replace(")", "\\)")
        body += f"BT /F1 10 Tf 50 {y} Td ({safe_line}) Tj ET\n"
        y -= 18

    stream_bytes = body.encode("latin1")
    stream_len = len(stream_bytes)

    pdf = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj
4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
5 0 obj << /Length {stream_len} >>
stream
{body}endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000222 00000 n 
0000000295 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
{350 + stream_len}
%%EOF
"""
    return pdf.encode("latin1")


@pytest.fixture(scope="module")
def auth_token_and_user():
    """Register and login a student for resume analysis tests."""
    reg_payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": TEST_USER_NAME,
        "college_name": "Apex Engineering Institute",
        "degree": "B.Tech",
        "branch": "Computer Science & Engineering"
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    if reg_res.status_code == 201:
        token = reg_res.json()["access_token"]
        user_id = reg_res.json()["user"]["id"]
    else:
        # Already registered, perform login
        login_res = client.post("/auth/login", json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
        token = login_res.json()["access_token"]
        user_id = login_res.json()["user"]["id"]

    headers = {"Authorization": f"Bearer {token}"}

    # Populate student profile with initial skills to test comparison
    client.put("/profile/me", headers=headers, json={
        "full_name": TEST_USER_NAME,
        "phone": "+91 9876543210",
        "technical_skills": ["Python", "FastAPI"],
        "programming_languages": ["Python"],
        "github_url": "https://github.com/alexanderwright",
        "linkedin_url": "https://linkedin.com/in/alexanderwright",
        "cgpa": 8.7
    })

    return {"headers": headers, "email": TEST_USER_EMAIL, "user_id": user_id}


# ============================================================================
# 1. TEXT EXTRACTION & NLP UNIT TESTS
# ============================================================================

def test_1_text_extraction_from_pdf_bytes():
    """Test PDF text extraction utility."""
    lines = [
        "Alexander Wright",
        "Email: alexander.wright@apextech.edu Phone: +91 9876543210",
        "Education: B.Tech Computer Science 2025",
        "Technical Skills: Python, FastAPI, React, Docker, PostgreSQL, Java, TypeScript"
    ]
    pdf_bytes = make_pdf_bytes(lines)
    extracted, method = extract_text_from_pdf_bytes(pdf_bytes)

    assert method in ["pdfplumber", "pypdf"]
    assert "Alexander Wright" in extracted
    assert "Python" in extracted
    assert "B.Tech" in extracted


def test_2_text_cleaning_pipeline():
    """Test clean_text handles whitespace, unicode dashes and empty lines."""
    raw = "Alexander   Wright  \n\n\n\n\u2022 Python \u2013 FastAPI \u2014 Docker   \n   \nPostgreSQL"
    cleaned = clean_text(raw)

    assert "   " not in cleaned
    assert "\u2022" not in cleaned
    assert "Python" in cleaned
    assert "FastAPI" in cleaned


def test_3_nlp_skill_extraction_accuracy():
    """Test boundary-safe keyword matching for programming languages and tools."""
    sample = (
        "Experienced in Python, Java, C++, TypeScript, and SQL. "
        "Built web services with FastAPI, React, Next.js, and Docker. "
        "Familiar with algorithm development and good design principles."
    )
    skills = extract_skills_from_text(sample)

    # Should match languages accurately
    assert "Python" in skills["programming_languages"]
    assert "Java" in skills["programming_languages"]
    assert "C++" in skills["programming_languages"]
    assert "SQL" in skills["programming_languages"]

    # Should NOT falsely match "go" inside "algorithm" or "good"
    assert "Go" not in skills["programming_languages"]

    # Technical skills
    assert "Fastapi" in skills["technical_skills"]
    assert "React" in skills["technical_skills"]
    assert "Docker" in skills["technical_skills"]


def test_4_nlp_profile_comparison_logic():
    """Test skill and profile missing info comparison."""
    resume_tech = ["React", "Docker", "PostgreSQL", "Kubernetes", "AWS"]
    resume_langs = ["Python", "JavaScript"]

    profile_data = {
        "technical_skills": ["Python", "FastAPI"],
        "programming_languages": ["Python"],
        "github_url": "https://github.com/alexwright",
        "resume_has_github": False,
        "linkedin_url": "https://linkedin.com/in/alexwright",
        "resume_has_linkedin": True
    }

    comp = compare_with_profile(resume_tech, resume_langs, profile_data)

    # Skills in resume but not in profile
    assert "Docker" in comp["skills_to_add_to_profile"]
    assert "Kubernetes" in comp["skills_to_add_to_profile"]
    assert "React" in comp["skills_to_add_to_profile"]

    # Skills in profile but not in resume
    assert "FastAPI" in comp["skills_missing_from_resume"]

    # Missing profile info in resume
    assert any("GitHub" in info for info in comp["missing_profile_info"])


# ============================================================================
# 2. API ENDPOINT & VALIDATION TESTS
# ============================================================================

def test_5_unauthenticated_resume_endpoints():
    """Test that resume endpoints reject unauthenticated access with 401."""
    res_upload = client.post("/resume/upload")
    assert res_upload.status_code == 401

    res_my = client.get("/resume/my-resume")
    assert res_my.status_code == 401

    res_analysis = client.get("/resume/analysis")
    assert res_analysis.status_code == 401


def test_6_resume_not_found_before_upload(auth_token_and_user):
    """Test GET /resume/my-resume returns 404 before any resume is uploaded."""
    headers = auth_token_and_user["headers"]
    res = client.get("/resume/my-resume", headers=headers)
    assert res.status_code == 404
    assert "No resume found" in res.json()["detail"]


def test_7_invalid_file_extension(auth_token_and_user):
    """Test that uploading a non-PDF file returns 400 Bad Request."""
    headers = auth_token_and_user["headers"]
    files = {
        "file": ("resume.txt", b"This is a plain text resume.", "text/plain")
    }
    res = client.post("/resume/upload", headers=headers, files=files)
    assert res.status_code == 400
    assert "Only .pdf files are supported" in res.json()["detail"] or "Invalid file" in res.json()["detail"]


def test_8_invalid_mime_type(auth_token_and_user):
    """Test uploading with an image MIME type returns 400 Bad Request."""
    headers = auth_token_and_user["headers"]
    files = {
        "file": ("resume.pdf", b"fake content", "image/png")
    }
    res = client.post("/resume/upload", headers=headers, files=files)
    assert res.status_code == 400
    assert "Only PDF files are accepted" in res.json()["detail"]


def test_9_empty_pdf_upload(auth_token_and_user):
    """Test that uploading an empty 0-byte PDF returns 400 Bad Request."""
    headers = auth_token_and_user["headers"]
    files = {
        "file": ("empty.pdf", b"", "application/pdf")
    }
    res = client.post("/resume/upload", headers=headers, files=files)
    assert res.status_code == 400
    assert "file is empty" in res.json()["detail"]


def test_10_corrupted_pdf_upload(auth_token_and_user):
    """Test that uploading corrupted non-PDF bytes returns 422 Unprocessable Entity."""
    headers = auth_token_and_user["headers"]
    files = {
        "file": ("corrupted.pdf", b"%PDF-1.4 CORRUPTED GARBAGE DATA WITH NO STRUCTURE", "application/pdf")
    }
    res = client.post("/resume/upload", headers=headers, files=files)
    assert res.status_code == 422
    assert "readable text" in res.json()["detail"] or "very little text" in res.json()["detail"]


def test_11_valid_pdf_upload_success(auth_token_and_user):
    """Test valid PDF resume upload, parsing, scoring, and DB persistence."""
    headers = auth_token_and_user["headers"]

    resume_lines = [
        "Alexander Wright",
        "Email: alexander.wright@apextech.edu",
        "Phone: +91 9876543210",
        "LinkedIn: linkedin.com/in/alexanderwright",
        "GitHub: github.com/alexanderwright",
        "Education",
        "B.Tech in Computer Science and Engineering 2025",
        "Apex Engineering Institute, CGPA: 8.7",
        "Technical Skills",
        "Python, Java, TypeScript, SQL, React, FastAPI, Docker, PostgreSQL, Kubernetes, AWS, Git",
        "Projects",
        "AI Career Twin Platform",
        "Engineered a digital twin platform using FastAPI, React, and PostgreSQL for placement prediction.",
        "Cloud Microservices Gateway",
        "Architected scalable microservices using Docker, Kubernetes, and AWS Lambda.",
        "Experience",
        "Software Engineer Intern at Microsoft (Jan 2024 - Jun 2024)",
        "Contributed to cloud services backend infrastructure using Python and Docker.",
        "Certifications",
        "AWS Certified Cloud Practitioner",
        "Summary",
        "Dedicated computer science student passionate about distributed cloud systems and machine learning."
    ]

    pdf_bytes = make_pdf_bytes(resume_lines)
    files = {
        "file": ("alexander_wright_resume.pdf", pdf_bytes, "application/pdf")
    }

    res = client.post("/resume/upload", headers=headers, files=files)
    assert res.status_code == 201

    data = res.json()
    assert data["file_name"] == "alexander_wright_resume.pdf"
    assert data["ats_score"] > 60.0
    assert data["ats_rating"] in ["Good", "Excellent"]
    assert "extracted_skills" in data
    assert "strengths" in data
    assert len(data["strengths"]) > 0

    # Skills present in resume but missing from profile
    assert "skills_to_add_to_profile" in data
    assert "Docker" in data["skills_to_add_to_profile"] or "Kubernetes" in data["skills_to_add_to_profile"]


def test_12_database_persistence_verification(auth_token_and_user):
    """Verify that resume record was persisted into database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == TEST_USER_EMAIL).first()
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        resume = db.query(Resume).filter(Resume.student_profile_id == profile.id).first()

        assert resume is not None
        assert resume.file_name == "alexander_wright_resume.pdf"
        assert resume.ats_score > 60.0
        assert resume.extracted_skills is not None
        assert "technical_skills" in resume.extracted_skills
        assert resume.extracted_skills["technical_skills"] is not None
        assert len(resume.extracted_skills["technical_skills"]) >= 5
    finally:
        db.close()


def test_13_get_my_resume_authenticated(auth_token_and_user):
    """Test GET /resume/my-resume returns latest resume metadata."""
    headers = auth_token_and_user["headers"]
    res = client.get("/resume/my-resume", headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["file_name"] == "alexander_wright_resume.pdf"
    assert data["ats_score"] > 60.0
    assert "uploaded_at" in data


def test_14_get_resume_analysis_authenticated(auth_token_and_user):
    """Test GET /resume/analysis returns full structured analysis and dynamic profile comparison."""
    headers = auth_token_and_user["headers"]
    res = client.get("/resume/analysis", headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["file_name"] == "alexander_wright_resume.pdf"
    assert data["ats_score"] > 60.0
    assert data["extracted_name"] == "Alexander Wright"
    assert data["extracted_email"] == "alexander.wright@apextech.edu"
    assert "alexanderwright" in (data["extracted_github"] or "")

    # Education
    assert len(data["education"]) >= 1
    assert data["education"][0]["degree"] in ["BTECH", "B.TECH"]

    # Technical skills
    assert "Docker" in data["technical_skills"]
    assert "Postgresql" in data["technical_skills"] or "PostgreSQL" in data["technical_skills"]

    # Projects
    assert len(data["projects"]) >= 1
    assert any("Career Twin" in p["title"] for p in data["projects"])

    # Experience & Internships
    assert len(data["internships"]) >= 1
    assert any("Microsoft" in i["company"] for i in data["internships"])

    # Certifications
    assert len(data["certifications"]) >= 1
    assert any("AWS" in c["title"] for c in data["certifications"])

    # ATS breakdown
    assert "ats_breakdown" in data
    assert "Skills & Languages" in data["ats_breakdown"]
    assert "Education" in data["ats_breakdown"]
    assert "Projects" in data["ats_breakdown"]

    # Profile comparison
    assert "skills_to_add_to_profile" in data
    assert "skills_missing_from_resume" in data
