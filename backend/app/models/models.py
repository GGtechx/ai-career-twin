import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    Date,
    ForeignKey,
    JSON,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Import User and StudentProfile from their dedicated modules
from app.models.user import User
from app.models.student_profile import StudentProfile


# ============================================================================
# 3. ACADEMIC RECORDS
# ============================================================================
class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    tenth_percentage = Column(Float, nullable=True)
    twelfth_percentage = Column(Float, nullable=True)
    cgpa = Column(Float, nullable=False, default=7.0)
    backlogs_active = Column(Integer, default=0, nullable=False)
    backlogs_history = Column(Integer, default=0, nullable=False)
    attendance_percentage = Column(Float, default=85.0, nullable=False)
    semester_gpas = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="academic_record")

    @property
    def active_backlogs(self) -> int:
        return self.backlogs_active or 0

    @active_backlogs.setter
    def active_backlogs(self, value: int):
        self.backlogs_active = value


# ============================================================================
# 4. SKILLS MASTER TABLE
# ============================================================================
class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    popularity_score = Column(Float, default=50.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student_skills = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")


# ============================================================================
# 5. STUDENT SKILLS (M:N Association with Metadata)
# ============================================================================
class StudentSkill(Base):
    __tablename__ = "student_skills"
    __table_args__ = (UniqueConstraint("student_profile_id", "skill_id", name="uq_student_skill"),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency_level = Column(String(30), default="Intermediate", nullable=False)
    proficiency_score = Column(Float, default=60.0)
    years_of_experience = Column(Float, default=1.0)
    verified_by = Column(String(50), default="Self")
    last_practiced = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="student_skills")
    skill = relationship("Skill", back_populates="student_skills")


# ============================================================================
# 6. PROJECTS
# ============================================================================
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)
    tech_stack = Column(JSON, nullable=True)
    github_url = Column(String(255), nullable=True)
    live_demo_url = Column(String(255), nullable=True)
    complexity_level = Column(String(30), default="Medium")
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile")


# ============================================================================
# 7. CERTIFICATIONS
# ============================================================================
class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    issuing_organization = Column(String(150), nullable=False)
    credential_id = Column(String(100), nullable=True)
    credential_url = Column(String(255), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    skills_covered = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile")


# ============================================================================
# 8. INTERNSHIPS
# ============================================================================
class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(150), nullable=False)
    role = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    duration_months = Column(Integer, default=3)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    stipend_monthly = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=True)
    certificate_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile")


# ============================================================================
# 9. CODING PERFORMANCE
# ============================================================================
class CodingPerformance(Base):
    __tablename__ = "coding_performance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    coding_skill_score = Column(Float, default=65.0)
    leetcode_solved_count = Column(Integer, default=0)
    leetcode_easy = Column(Integer, default=0)
    leetcode_medium = Column(Integer, default=0)
    leetcode_hard = Column(Integer, default=0)
    codeforces_rating = Column(Integer, nullable=True)
    hackerrank_stars = Column(Integer, default=0)
    github_repos_count = Column(Integer, default=0)
    hackathons_participated = Column(Integer, default=0)
    languages_breakdown = Column(JSON, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile")


# ============================================================================
# 10. APTITUDE PERFORMANCE
# ============================================================================
class AptitudePerformance(Base):
    __tablename__ = "aptitude_performance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    quantitative_score = Column(Float, default=65.0)
    logical_reasoning_score = Column(Float, default=65.0)
    verbal_communication_score = Column(Float, default=65.0)
    mock_interview_score = Column(Float, default=65.0)
    overall_aptitude_score = Column(Float, default=65.0)
    tests_completed_count = Column(Integer, default=0)
    percentile = Column(Float, default=50.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile")


# ============================================================================
# 11. RESUMES
# ============================================================================
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    parsed_text = Column(Text, nullable=True)
    ats_score = Column(Float, default=0.0)
    extracted_skills = Column(JSON, nullable=True)
    extracted_experience_years = Column(Float, default=0.0)
    formatting_score = Column(Float, default=0.0)
    strengths = Column(JSON, nullable=True)
    improvements_suggested = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="resumes")


# ============================================================================
# 12. COMPANIES
# ============================================================================
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    industry = Column(String(100), nullable=True)
    tier = Column(String(30), default="Tier 1")
    website = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)
    hiring_status = Column(String(50), default="Active")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    job_roles = relationship("JobRole", back_populates="company", cascade="all, delete-orphan")


# ============================================================================
# 13. JOB ROLES
# ============================================================================
class JobRole(Base):
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), index=True, nullable=False)
    domain = Column(String(100), nullable=False)
    role_type = Column(String(50), default="Full-Time")
    experience_level = Column(String(50), default="Entry-Level")
    package_min_lpa = Column(Float, nullable=True)
    package_max_lpa = Column(Float, nullable=True)
    location = Column(String(100), default="Bengaluru / Hybrid")
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    company = relationship("Company", back_populates="job_roles")
    job_requirement = relationship("JobRequirement", back_populates="job_role", uselist=False, cascade="all, delete-orphan")
    skill_gap_results = relationship("SkillGapResult", back_populates="job_role", cascade="all, delete-orphan")
    career_roadmaps = relationship("CareerRoadmap", back_populates="job_role")


# ============================================================================
# 14. JOB REQUIREMENTS
# ============================================================================
class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="CASCADE"), unique=True, nullable=False)
    min_cgpa = Column(Float, default=7.0)
    max_active_backlogs = Column(Integer, default=0)
    eligible_branches = Column(JSON, nullable=True)
    must_have_skills = Column(JSON, nullable=False)
    good_to_have_skills = Column(JSON, nullable=True)
    min_internships_count = Column(Integer, default=0)
    min_projects_count = Column(Integer, default=2)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    job_role = relationship("JobRole", back_populates="job_requirement")


# ============================================================================
# 15. SKILL GAP RESULTS
# ============================================================================
class SkillGapResult(Base):
    __tablename__ = "skill_gap_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False)
    match_percentage = Column(Float, nullable=False)
    matching_skills = Column(JSON, nullable=True)
    missing_critical_skills = Column(JSON, nullable=True)
    missing_secondary_skills = Column(JSON, nullable=True)
    readiness_tier = Column(String(50), default="Moderate")
    analysis_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="skill_gap_results")
    job_role = relationship("JobRole", back_populates="skill_gap_results")


# ============================================================================
# 16. PLACEMENT READINESS
# ============================================================================
class PlacementReadiness(Base):
    __tablename__ = "placement_readiness"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    readiness_score = Column(Float, nullable=False)
    predicted_status = Column(String(30), nullable=False)
    placement_probability = Column(Float, nullable=False)
    predicted_salary_min_lpa = Column(Float, nullable=True)
    predicted_salary_max_lpa = Column(Float, nullable=True)
    confidence_score = Column(Float, default=0.88)
    top_positive_factors = Column(JSON, nullable=True)
    top_risk_factors = Column(JSON, nullable=True)
    model_version = Column(String(50), default="v1.0-basepaper")
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="placement_readiness")


# ============================================================================
# 17. COURSES
# ============================================================================
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    provider = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    domain = Column(String(100), nullable=True)
    difficulty_level = Column(String(30), default="Beginner")
    duration_hours = Column(Float, nullable=True)
    rating = Column(Float, default=4.5)
    is_free = Column(Boolean, default=True)
    mapped_skills = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    recommendations = relationship("Recommendation", back_populates="course")


# ============================================================================
# 18. CAREER ROADMAPS
# ============================================================================
class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    target_timeline_weeks = Column(Integer, default=12)
    current_week = Column(Integer, default=1)
    total_milestones = Column(Integer, default=4)
    completed_milestones = Column(Integer, default=0)
    roadmap_data = Column(JSON, nullable=False)
    status = Column(String(30), default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="career_roadmaps")
    job_role = relationship("JobRole", back_populates="career_roadmaps")


# ============================================================================
# 19. RECOMMENDATIONS
# ============================================================================
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="Medium")
    action_url = Column(String(500), nullable=True)
    is_completed = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="recommendations")
    course = relationship("Course", back_populates="recommendations")


# ============================================================================
# 20. DIGITAL CAREER TWIN
# ============================================================================
class DigitalCareerTwin(Base):
    __tablename__ = "digital_career_twin"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    twin_name = Column(String(100), default="Career Twin Alpha")
    twin_version = Column(Integer, default=1)
    coding_score = Column(Float, default=65.0)
    aptitude_score = Column(Float, default=65.0)
    communication_score = Column(Float, default=65.0)
    logical_score = Column(Float, default=65.0)
    leadership_score = Column(Float, default=55.0)
    project_score = Column(Float, default=60.0)
    overall_twin_score = Column(Float, default=62.5)
    benchmark_percentile = Column(Float, default=50.0)
    projected_placement_chance = Column(Float, default=55.0)
    projected_salary_lpa = Column(Float, default=7.5)
    simulation_state = Column(JSON, nullable=True)
    radar_history = Column(JSON, nullable=True)
    last_simulated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="digital_career_twin")


# ============================================================================
# 21. PROGRESS TRACKING
# ============================================================================
class ProgressTracking(Base):
    __tablename__ = "progress_tracking"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    item_title = Column(String(200), nullable=False)
    status = Column(String(30), default="Not Started")
    completion_percentage = Column(Float, default=0.0)
    score_obtained = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    logged_date = Column(Date, default=datetime.date.today)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student_profile = relationship("StudentProfile", back_populates="progress_tracking")
