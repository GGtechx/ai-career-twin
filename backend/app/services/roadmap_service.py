"""
Personalized Career Roadmap Service
Generates and manages multi-stage roadmaps (7 core stages) synthesized from
Student Profile, Target Job, Skill Gap, Placement Readiness, and Recommendations.
Stores state and task progression in career_roadmaps and progress_tracking tables.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.models import (
    CareerRoadmap, ProgressTracking, JobRole, SkillGapResult,
    PlacementReadiness, Recommendation
)
from app.models.student_profile import StudentProfile
from app.models.user import User

logger = logging.getLogger("app.services.roadmap_service")

# 7 Canonical Roadmap Stages
STAGE_DEFINITIONS = [
    {
        "stage_number": 1,
        "stage_name": "Skill Foundation",
        "description": "Establish core language syntax, programming fundamentals, and database query mastery."
    },
    {
        "stage_number": 2,
        "stage_name": "Skill Development",
        "description": "Deep-dive into modern frameworks, libraries, APIs, and containerized architectures."
    },
    {
        "stage_number": 3,
        "stage_name": "Project Development",
        "description": "Build, test, and deploy production-ready full-stack or AI capstone applications."
    },
    {
        "stage_number": 4,
        "stage_name": "Certification",
        "description": "Attain industry-standard credentials to validate specialized competencies."
    },
    {
        "stage_number": 5,
        "stage_name": "Coding & Aptitude",
        "description": "Daily competitive coding, data structures, algorithm drills, and quantitative problem solving."
    },
    {
        "stage_number": 6,
        "stage_name": "Interview Preparation",
        "description": "Master system design principles, technical architecture, and STAR-format behavioral drills."
    },
    {
        "stage_number": 7,
        "stage_name": "Placement Ready",
        "description": "Final resume optimization, mock company rounds, and professional outreach."
    }
]


def generate_career_roadmap(
    db: Session,
    user: User,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Generates a personalized 7-stage career roadmap for the student.
    Persists roadmap in career_roadmaps table.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found. Please complete profile first.")

    # Check existing active roadmap
    existing = db.query(CareerRoadmap).filter(
        CareerRoadmap.student_profile_id == profile.id,
        CareerRoadmap.status == "Active"
    ).order_by(CareerRoadmap.created_at.desc()).first()

    if existing and not force_refresh:
        return _format_roadmap_response(existing, profile)

    # Gather inputs
    # 1. Fetch latest context aligned with active target job
    target_job = None
    if profile.target_job_role:
        from app.models.models import JobRole, Company
        if profile.target_company:
            target_job = db.query(JobRole).join(Company).filter(
                JobRole.title == profile.target_job_role,
                Company.name == profile.target_company
            ).first()
        if not target_job:
            target_job = db.query(JobRole).filter(JobRole.title == profile.target_job_role).first()

    gap_query = db.query(SkillGapResult).filter(SkillGapResult.student_profile_id == profile.id)
    if target_job:
        latest_gap = gap_query.filter(SkillGapResult.job_role_id == target_job.id).order_by(SkillGapResult.created_at.desc()).first()
        if not latest_gap:
            try:
                from app.services.skill_gap_service import analyze_skill_gap
                analyze_skill_gap(db, user, target_job.id)
                latest_gap = gap_query.filter(SkillGapResult.job_role_id == target_job.id).order_by(SkillGapResult.created_at.desc()).first()
            except Exception:
                pass
    else:
        latest_gap = gap_query.order_by(SkillGapResult.created_at.desc()).first()

    latest_readiness = db.query(PlacementReadiness).filter(
        PlacementReadiness.student_profile_id == profile.id
    ).order_by(PlacementReadiness.assessed_at.desc()).first()

    target_job_title = (target_job.title if target_job else profile.target_job_role) or "Software Development Engineer"
    target_company_name = (target_job.company.name if (target_job and target_job.company) else profile.target_company) or "Target Tech Corp"

    missing_critical = list(latest_gap.missing_critical_skills or []) if latest_gap else []
    missing_secondary = list(latest_gap.missing_secondary_skills or []) if latest_gap else []

    top_missing_1 = missing_critical[0] if len(missing_critical) > 0 else "System Architecture"
    top_missing_2 = missing_critical[1] if len(missing_critical) > 1 else "Cloud Services"

    # Build 7 stages with personalized tasks
    stages_data = []

    # 1. Skill Foundation
    stages_data.append({
        "stage_number": 1,
        "stage_name": "Skill Foundation",
        "description": STAGE_DEFINITIONS[0]["description"],
        "items": [
            {
                "item_id": "sf_1",
                "stage": "Skill Foundation",
                "title": f"Master {top_missing_1} & Core Language Fundamentals",
                "description": f"Solidify syntax, object-oriented concepts, and memory management for {top_missing_1}.",
                "priority": "High",
                "estimated_duration": "Week 1 - 2",
                "status": "Not Started",
                "completion_percentage": 0.0
            },
            {
                "item_id": "sf_2",
                "stage": "Skill Foundation",
                "title": "Relational Database Design & Complex SQL Querying",
                "description": "Write normalized schemas, indexes, transactions, and join queries with PostgreSQL.",
                "priority": "Medium",
                "estimated_duration": "Week 2 - 3",
                "status": "Not Started",
                "completion_percentage": 0.0
            }
        ]
    })

    # 2. Skill Development
    stages_data.append({
        "stage_number": 2,
        "stage_name": "Skill Development",
        "description": STAGE_DEFINITIONS[1]["description"],
        "items": [
            {
                "item_id": "sd_1",
                "stage": "Skill Development",
                "title": f"Implement Modern Frameworks ({top_missing_2})",
                "description": f"Build modular REST APIs, routing, middleware, and authentication with {top_missing_2}.",
                "priority": "High",
                "estimated_duration": "Week 3 - 4",
                "status": "Not Started",
                "completion_percentage": 0.0
            },
            {
                "item_id": "sd_2",
                "stage": "Skill Development",
                "title": "Containerization & Docker Orchestration",
                "description": "Create multi-stage Dockerfiles and compose setups for localized microservices testing.",
                "priority": "Medium",
                "estimated_duration": "Week 4 - 5",
                "status": "Not Started",
                "completion_percentage": 0.0
            }
        ]
    })

    # 3. Project Development
    stages_data.append({
        "stage_number": 3,
        "stage_name": "Project Development",
        "description": STAGE_DEFINITIONS[2]["description"],
        "items": [
            {
                "item_id": "pd_1",
                "stage": "Project Development",
                "title": f"Build & Deploy {target_job_title} Capstone Project",
                "description": f"Architect a complete cloud-hosted web platform solving an industry problem with live public URL.",
                "priority": "High",
                "estimated_duration": "Week 5 - 7",
                "status": "Not Started",
                "completion_percentage": 0.0
            },
            {
                "item_id": "pd_2",
                "stage": "Project Development",
                "title": "Publish Comprehensive GitHub Repository & Documentation",
                "description": "Write clear README, architectural diagram, API documentation, and unit tests.",
                "priority": "Medium",
                "estimated_duration": "Week 7",
                "status": "Not Started",
                "completion_percentage": 0.0
            }
        ]
    })

    # 4. Certification
    stages_data.append({
        "stage_number": 4,
        "stage_name": "Certification",
        "description": STAGE_DEFINITIONS[3]["description"],
        "items": [
            {
                "item_id": "cert_1",
                "stage": "Certification",
                "title": "Clear Industry Certification (AWS / Google / Coursera)",
                "description": f"Gain accredited credential to distinguish your profile during {target_company_name} screening.",
                "priority": "Medium",
                "estimated_duration": "Week 7 - 8",
                "status": "Not Started",
                "completion_percentage": 0.0
            }
        ]
    })

    # 5. Coding & Aptitude
    stages_data.append({
        "stage_number": 5,
        "stage_name": "Coding & Aptitude",
        "description": STAGE_DEFINITIONS[4]["description"],
        "items": [
            {
                "item_id": "ca_1",
                "stage": "Coding & Aptitude",
                "title": "Solve 75 High-Frequency LeetCode / DSA Problems",
                "description": "Focus on Arrays, Two Pointers, Sliding Window, Trees, Graphs, and Dynamic Programming.",
                "priority": "High",
                "estimated_duration": "Week 8 - 10",
                "status": "Not Started",
                "completion_percentage": 0.0
            },
            {
                "item_id": "ca_2",
                "stage": "Coding & Aptitude",
                "title": "Daily Quantitative Aptitude & Logical Reasoning Tests",
                "description": "Practice time-bound mock quizzes covering speed math, probability, and analytical reasoning.",
                "priority": "High",
                "estimated_duration": "Week 9 - 10",
                "status": "Not Started",
                "completion_percentage": 0.0
            }
        ]
    })

    # 6. Interview Preparation
    stages_data.append({
        "stage_number": 6,
        "stage_name": "Interview Preparation",
        "description": STAGE_DEFINITIONS[5]["description"],
        "items": [
            {
                "item_id": "ip_1",
                "stage": "Interview Preparation",
                "title": "System Design & Architecture Walkthroughs",
                "description": "Study caching, load balancing, database sharding, and latency optimization patterns.",
                "priority": "High",
                "estimated_duration": "Week 10 - 11",
                "status": "Not Started",
                "completion_percentage": 0.0
            },
            {
                "item_id": "ip_2",
                "stage": "Interview Preparation",
                "title": "Conduct 3 Peer Mock Technical & Behavioral Interviews",
                "description": "Simulate technical coding interviews and practice STAR behavioral stories.",
                "priority": "High",
                "estimated_duration": "Week 11",
                "status": "Not Started",
                "completion_percentage": 0.0
            }
        ]
    })

    # 7. Placement Ready
    stages_data.append({
        "stage_number": 7,
        "stage_name": "Placement Ready",
        "description": STAGE_DEFINITIONS[6]["description"],
        "items": [
            {
                "item_id": "pr_1",
                "stage": "Placement Ready",
                "title": f"Tailor Resume for {target_company_name} ATS Requirements",
                "description": "Align keywords, showcase measurable metrics (X% faster, Y users), and re-run ATS analyzer.",
                "priority": "High",
                "estimated_duration": "Week 12",
                "status": "Not Started",
                "completion_percentage": 0.0
            },
            {
                "item_id": "pr_2",
                "stage": "Placement Ready",
                "title": "Apply to Campus Drives & Target Corporate Openings",
                "description": "Leverage alumni referrals and submit well-crafted cover notes.",
                "priority": "High",
                "estimated_duration": "Week 12+",
                "status": "Not Started",
                "completion_percentage": 0.0
            }
        ]
    })

    # Save into DB
    roadmap_title = f"12-Week Placement Roadmap: {target_job_title} at {target_company_name}"
    total_tasks = sum(len(s["items"]) for s in stages_data)

    if existing and force_refresh:
        existing.title = roadmap_title
        existing.job_role_id = target_job.id if target_job else None
        existing.roadmap_data = stages_data
        existing.total_milestones = total_tasks
        existing.completed_milestones = 0
        roadmap = existing
    else:
        roadmap = CareerRoadmap(
            student_profile_id=profile.id,
            job_role_id=target_job.id if target_job else None,
            title=roadmap_title,
            target_timeline_weeks=12,
            current_week=1,
            total_milestones=total_tasks,
            completed_milestones=0,
            roadmap_data=stages_data,
            status="Active"
        )
        db.add(roadmap)

    db.commit()
    db.refresh(roadmap)

    return _format_roadmap_response(roadmap, profile)


def _format_roadmap_response(roadmap: CareerRoadmap, profile: StudentProfile) -> Dict[str, Any]:
    stages_data = roadmap.roadmap_data or []
    total_tasks = 0
    completed_tasks = 0

    formatted_stages = []
    for s in stages_data:
        items = s.get("items", [])
        total_tasks += len(items)
        stage_comp = len([i for i in items if i.get("status") == "Completed"])
        completed_tasks += stage_comp
        stage_pct = round((stage_comp / max(len(items), 1)) * 100.0, 1)

        formatted_stages.append({
            "stage_number": s.get("stage_number"),
            "stage_name": s.get("stage_name"),
            "description": s.get("description", ""),
            "items": items,
            "stage_progress_percentage": stage_pct
        })

    overall_pct = round((completed_tasks / max(total_tasks, 1)) * 100.0, 1)

    target_title = roadmap.job_role.title if roadmap.job_role else (profile.target_job_role or "Target Job")
    target_comp = roadmap.job_role.company.name if roadmap.job_role and roadmap.job_role.company else (profile.target_company or "Target Company")

    return {
        "id": roadmap.id,
        "student_profile_id": roadmap.student_profile_id,
        "job_role_id": roadmap.job_role_id,
        "target_job_title": target_title,
        "target_company_name": target_comp,
        "title": roadmap.title,
        "target_timeline_weeks": roadmap.target_timeline_weeks,
        "current_week": roadmap.current_week,
        "overall_progress_percentage": overall_pct,
        "stages": formatted_stages,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "created_at": roadmap.created_at,
        "updated_at": roadmap.updated_at
    }


def update_task_progress(
    db: Session,
    user: User,
    item_id: str,
    status: str,
    completion_percentage: Optional[float] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Updates the completion status of a specific task item in the roadmap
    and logs progress tracking into the progress_tracking database table.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Profile not found.")

    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.student_profile_id == profile.id,
        CareerRoadmap.status == "Active"
    ).order_by(CareerRoadmap.created_at.desc()).first()

    if not roadmap:
        raise ValueError("No active career roadmap found.")

    import copy
    from sqlalchemy.orm.attributes import flag_modified

    stages = copy.deepcopy(roadmap.roadmap_data or [])
    item_found = None
    item_category = "General"

    for s in stages:
        for itm in s.get("items", []):
            if itm.get("item_id") == item_id:
                itm["status"] = status
                if completion_percentage is not None:
                    itm["completion_percentage"] = completion_percentage
                elif status == "Completed":
                    itm["completion_percentage"] = 100.0
                elif status == "Not Started":
                    itm["completion_percentage"] = 0.0

                item_found = itm
                item_category = s.get("stage_name", "General")
                break
        if item_found:
            break

    if not item_found:
        raise ValueError(f"Task with ID '{item_id}' not found in current roadmap.")

    # Re-calculate overall stats
    total_tasks = sum(len(s.get("items", [])) for s in stages)
    completed_tasks = sum(
        len([i for i in s.get("items", []) if i.get("status") == "Completed"])
        for s in stages
    )

    roadmap.roadmap_data = stages
    flag_modified(roadmap, "roadmap_data")
    roadmap.completed_milestones = completed_tasks
    roadmap.total_milestones = total_tasks
    roadmap.updated_at = datetime.utcnow()

    # Log in progress_tracking table
    tracking = ProgressTracking(
        student_profile_id=profile.id,
        category=item_category,
        item_title=item_found.get("title", item_id),
        status=status,
        completion_percentage=item_found.get("completion_percentage", 0.0),
        notes=notes or f"Updated task status to {status}",
        logged_date=date.today()
    )
    db.add(tracking)

    db.commit()
    db.refresh(roadmap)

    return _format_roadmap_response(roadmap, profile)


def get_student_career_roadmap(
    db: Session,
    user: User
) -> Dict[str, Any]:
    """Retrieves existing active roadmap or generates a new one."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Profile not found.")

    # Find active target job to check if cached roadmap is aligned
    target_job = None
    if profile.target_job_role:
        from app.models.models import JobRole, Company
        if profile.target_company:
            target_job = db.query(JobRole).join(Company).filter(
                JobRole.title == profile.target_job_role,
                Company.name == profile.target_company
            ).first()
        if not target_job:
            target_job = db.query(JobRole).filter(JobRole.title == profile.target_job_role).first()

    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.student_profile_id == profile.id,
        CareerRoadmap.status == "Active"
    ).order_by(CareerRoadmap.created_at.desc()).first()

    if not roadmap:
        return generate_career_roadmap(db, user)

    # If the active target job changed and does not match the active roadmap, auto-regenerate
    if target_job and roadmap.job_role_id != target_job.id:
        return generate_career_roadmap(db, user, force_refresh=True)

    return _format_roadmap_response(roadmap, profile)
