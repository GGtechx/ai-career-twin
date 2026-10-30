from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, index=True, nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    
    # Academics
    college_name = Column(String(255), nullable=True)
    college_tier = Column(String(20), default="Tier 2", nullable=True)
    degree = Column(String(100), default="B.Tech", nullable=True)  # B.Tech, B.E., BCA, MCA, M.Tech, etc.
    branch = Column(String(100), default="CSE", nullable=True)
    cgpa = Column(Float, default=0.0, nullable=False)
    graduation_year = Column(Integer, nullable=True)
    current_year = Column(Integer, default=3, nullable=True)
    current_semester = Column(Integer, default=6, nullable=True)

    # Skills & Performance Scores
    technical_skills = Column(JSON, default=list)        # ["FastAPI", "React", "Docker", "PostgreSQL"]
    soft_skills = Column(JSON, default=list)             # ["Leadership", "Problem Solving", "Teamwork"]
    programming_languages = Column(JSON, default=list)   # ["Python", "JavaScript", "C++"]
    coding_score = Column(Float, default=0.0)            # 0 to 100
    aptitude_score = Column(Float, default=0.0)          # 0 to 100
    communication_score = Column(Float, default=0.0)     # 0 to 100

    # Portfolio & Experience JSON structures
    projects = Column(JSON, default=list)                # [{"title": "...", "tech_stack": [...], "desc": "..."}]
    certifications = Column(JSON, default=list)          # [{"title": "...", "issuer": "...", "date": "..."}]
    internships = Column(JSON, default=list)             # [{"company": "...", "role": "...", "duration": "..."}]

    # Career Vision & Targeting
    interests = Column(JSON, default=list)               # ["AI/ML", "Cloud Systems", "Full-Stack Web"]
    career_goal = Column(Text, nullable=True)            # e.g., "Become a Senior Backend Architect"
    target_company = Column(String(150), nullable=True)  # e.g., "Google"
    target_job_role = Column(String(150), nullable=True) # e.g., "Software Development Engineer"

    # Social & Links
    bio = Column(Text, nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    leetcode_url = Column(String(255), nullable=True)
    portfolio_url = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    academic_record = relationship("AcademicRecord", back_populates="student_profile", uselist=False, cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="student_profile", cascade="all, delete-orphan")
    digital_career_twin = relationship("DigitalCareerTwin", back_populates="student_profile", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="student_profile", cascade="all, delete-orphan")
    skill_gap_results = relationship("SkillGapResult", back_populates="student_profile", cascade="all, delete-orphan")
    placement_readiness = relationship("PlacementReadiness", back_populates="student_profile", cascade="all, delete-orphan")
    career_roadmaps = relationship("CareerRoadmap", back_populates="student_profile", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="student_profile", cascade="all, delete-orphan")
    progress_tracking = relationship("ProgressTracking", back_populates="student_profile", cascade="all, delete-orphan")
