import pytest
import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import inspect, text
from app.core.database import engine, Base, SessionLocal
import app.models as models

EXPECTED_TABLES = {
    "users",
    "student_profiles",
    "academic_records",
    "skills",
    "student_skills",
    "projects",
    "certifications",
    "internships",
    "coding_performance",
    "aptitude_performance",
    "resumes",
    "companies",
    "job_roles",
    "job_requirements",
    "skill_gap_results",
    "placement_readiness",
    "courses",
    "career_roadmaps",
    "recommendations",
    "digital_career_twin",
    "progress_tracking"
}

def test_database_connection():
    """Verify that the engine can establish a live connection."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_all_21_models_registered():
    """Verify all 21 models are properly registered in SQLAlchemy metadata."""
    registered = set(Base.metadata.tables.keys())
    missing = EXPECTED_TABLES - registered
    assert len(missing) == 0, f"Missing registered models: {missing}"
    assert len(registered) == 21

def test_create_all_tables():
    """Verify all 21 tables can be created cleanly in the database."""
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    created_tables = set(inspector.get_table_names())
    missing = EXPECTED_TABLES - created_tables
    assert len(missing) == 0, f"Tables missing in database: {missing}"

def test_insert_and_query_relationships():
    """
    Test creating a user, student profile, digital twin, academic record,
    and verifying cascading relationships.
    """
    db = SessionLocal()
    try:
        # Create user
        test_email = "alex.chen@university.edu"
        existing = db.query(models.User).filter_by(email=test_email).first()
        if existing:
            db.delete(existing)
            db.commit()

        user = models.User(
            email=test_email,
            password_hash="fake_bcrypt_hash_for_testing",
            full_name="Alex Chen",
            role="student"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.id is not None

        # Create Profile
        profile = models.StudentProfile(
            user_id=user.id,
            roll_number="CS2026-001",
            college_name="Apex Institute of Technology",
            college_tier="Tier 1",
            branch="CSE",
            current_year=4,
            current_semester=7
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        assert profile.id is not None
        assert profile.user.full_name == "Alex Chen"

        # Create Academic Record
        academic = models.AcademicRecord(
            student_profile_id=profile.id,
            cgpa=8.75,
            backlogs_active=0,
            attendance_percentage=92.5
        )
        db.add(academic)

        # Create Digital Career Twin
        twin = models.DigitalCareerTwin(
            student_profile_id=profile.id,
            twin_name="Alex's AI Twin",
            coding_score=85.0,
            aptitude_score=80.0,
            communication_score=78.0,
            logical_score=82.0,
            leadership_score=70.0,
            project_score=88.0,
            benchmark_percentile=84.5,
            projected_placement_chance=89.2,
            projected_salary_lpa=14.5
        )
        db.add(twin)

        # Create Skill & Student Skill
        skill = db.query(models.Skill).filter_by(name="Python").first()
        if not skill:
            skill = models.Skill(name="Python", category="Programming", popularity_score=95.0)
            db.add(skill)
            db.commit()
            db.refresh(skill)

        student_skill = models.StudentSkill(
            student_profile_id=profile.id,
            skill_id=skill.id,
            proficiency_level="Advanced",
            proficiency_score=88.0
        )
        db.add(student_skill)
        db.commit()

        # Query and assert relationships
        queried_profile = db.query(models.StudentProfile).filter_by(id=profile.id).first()
        assert queried_profile.academic_record.cgpa == 8.75
        assert queried_profile.digital_career_twin.coding_score == 85.0
        assert len(queried_profile.student_skills) == 1
        assert queried_profile.student_skills[0].skill.name == "Python"

        print("\nAll relationship assertions passed successfully!")
    finally:
        db.close()
