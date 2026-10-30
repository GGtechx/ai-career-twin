import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.models import (
    Resume, JobRole, Company, SkillGapResult,
    PlacementReadiness, CareerRoadmap, DigitalCareerTwin,
    Recommendation
)
from app.schemas.dashboard import (
    StudentDashboardResponse, DashboardProfileSummary, DashboardResumeSummary,
    DashboardTargetJobSummary, DashboardSkillGapSummary, DashboardPlacementSummary,
    DashboardRoadmapSummary, DashboardTwinSummary, DashboardActionItem
)
from app.services.career_twin_service import get_or_create_twin

logger = logging.getLogger("app.services.dashboard_service")


def get_student_dashboard_summary(db: Session, user: User) -> StudentDashboardResponse:
    """
    Compiles complete live telemetry for the student's main dashboard:
    Profile, Resume, Target Job, Skill Gaps, Placement Readiness, Roadmap, Career Twin, and Next Actions.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # 1. Profile Summary
    prof_summary = DashboardProfileSummary(
        user_id=user.id,
        full_name=user.full_name or "Student",
        email=user.email,
        college_name=profile.college_name,
        degree=profile.degree or "B.Tech",
        branch=profile.branch or "Computer Science",
        cgpa=float(profile.cgpa or 7.5),
        technical_skills=list(profile.technical_skills or []),
        projects_count=len(profile.projects or []),
        certifications_count=len(profile.certifications or []),
        internships_count=len(profile.internships or []),
        coding_score=float(profile.coding_score or 65.0),
        aptitude_score=float(profile.aptitude_score or 65.0)
    )

    # 2. Resume Summary
    latest_resume = db.query(Resume).filter(
        Resume.student_profile_id == profile.id
    ).order_by(Resume.uploaded_at.desc()).first()

    resume_summary = DashboardResumeSummary()
    if latest_resume:
        ats = float(latest_resume.ats_score or 0.0)
        rating = "Excellent" if ats >= 80 else "Good" if ats >= 65 else "Needs Work"
        skills_len = len(latest_resume.extracted_skills or [])
        resume_summary = DashboardResumeSummary(
            has_resume=True,
            file_name=latest_resume.file_name,
            ats_score=ats,
            ats_rating=rating,
            extracted_skills_count=skills_len,
            uploaded_at=latest_resume.uploaded_at
        )

    # 3. Target Job Summary
    target_summary = DashboardTargetJobSummary()
    if profile.target_job_role:
        job = db.query(JobRole).filter(JobRole.title == profile.target_job_role).first()
        comp_tier = "Tier 1"
        if job and job.company:
            comp_tier = job.company.tier or "Tier 1"
        target_summary = DashboardTargetJobSummary(
            has_target=True,
            target_company=profile.target_company or "Target Company",
            target_job_role=profile.target_job_role,
            target_job_id=job.id if job else None,
            tier=comp_tier
        )

    # 4. Skill Gap Summary aligned with active target job
    gap_query = db.query(SkillGapResult).filter(SkillGapResult.student_profile_id == profile.id)
    if target_summary.target_job_id:
        latest_gap = gap_query.filter(SkillGapResult.job_role_id == target_summary.target_job_id).order_by(SkillGapResult.created_at.desc()).first()
        if not latest_gap:
            try:
                from app.services.skill_gap_service import analyze_skill_gap
                analyze_skill_gap(db, user, target_summary.target_job_id)
                latest_gap = gap_query.filter(SkillGapResult.job_role_id == target_summary.target_job_id).order_by(SkillGapResult.created_at.desc()).first()
            except Exception:
                pass
    else:
        latest_gap = gap_query.order_by(SkillGapResult.created_at.desc()).first()

    gap_summary = DashboardSkillGapSummary()
    if latest_gap:
        gap_summary = DashboardSkillGapSummary(
            has_analysis=True,
            match_percentage=float(latest_gap.match_percentage or 0.0),
            readiness_tier=latest_gap.readiness_tier or "Moderate",
            matched_skills_count=len(latest_gap.matching_skills or []),
            missing_critical_skills=list(latest_gap.missing_critical_skills or [])[:4],
            missing_secondary_skills=list(latest_gap.missing_secondary_skills or [])[:3]
        )

    # 5. Placement Readiness Summary
    latest_readiness = db.query(PlacementReadiness).filter(
        PlacementReadiness.student_profile_id == profile.id
    ).order_by(PlacementReadiness.assessed_at.desc()).first()

    placement_summary = DashboardPlacementSummary()
    if latest_readiness:
        category = "Placement Ready (High)" if latest_readiness.readiness_score >= 75 else "Moderate Readiness" if latest_readiness.readiness_score >= 60 else "At Risk"
        placement_summary = DashboardPlacementSummary(
            has_prediction=True,
            readiness_score=float(latest_readiness.readiness_score or 65.0),
            readiness_category=category,
            predicted_status=latest_readiness.predicted_status or "Placed",
            placement_probability=float(latest_readiness.placement_probability or 0.65),
            predicted_salary_min_lpa=latest_readiness.predicted_salary_min_lpa or 7.5,
            predicted_salary_max_lpa=latest_readiness.predicted_salary_max_lpa or 12.0,
            top_strengths=list(latest_readiness.top_positive_factors or [])[:3],
            top_risk_factors=list(latest_readiness.top_risk_factors or [])[:2]
        )

    # 6. Roadmap Summary aligned with active target job
    roadmap_query = db.query(CareerRoadmap).filter(
        CareerRoadmap.student_profile_id == profile.id,
        CareerRoadmap.status == "Active"
    )
    if target_summary.target_job_id:
        active_roadmap = roadmap_query.filter(CareerRoadmap.job_role_id == target_summary.target_job_id).order_by(CareerRoadmap.created_at.desc()).first()
        if not active_roadmap:
            active_roadmap = roadmap_query.order_by(CareerRoadmap.created_at.desc()).first()
    else:
        active_roadmap = roadmap_query.order_by(CareerRoadmap.created_at.desc()).first()

    roadmap_summary = DashboardRoadmapSummary()
    if active_roadmap:
        total_tasks = 0
        completed_tasks = 0
        current_stage = "Skill Foundation"
        stages = list(active_roadmap.roadmap_data or [])
        found_stage = False

        for s in stages:
            items = s.get("items", [])
            total_tasks += len(items)
            completed_tasks += len([i for i in items if i.get("status") == "Completed"])
            if not found_stage and any(i.get("status") != "Completed" for i in items):
                current_stage = s.get("stage_name", "Skill Foundation")
                found_stage = True

        overall_pct = round((completed_tasks / max(total_tasks, 1)) * 100.0, 1)
        roadmap_summary = DashboardRoadmapSummary(
            has_roadmap=True,
            current_stage=current_stage,
            overall_progress_percentage=overall_pct,
            completed_milestones=completed_tasks,
            total_milestones=total_tasks,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks
        )

    # 7. Digital Career Twin Summary
    twin = get_or_create_twin(db, user)
    twin_summary = DashboardTwinSummary(
        has_twin=True,
        twin_name=twin.twin_name,
        twin_version=twin.twin_version or 1,
        overall_twin_score=float(twin.overall_twin_score or 64.0),
        benchmark_percentile=float(twin.benchmark_percentile or 50.0),
        projected_salary_lpa=float(twin.projected_salary_lpa or 7.5),
        radar_breakdown={
            "Coding": float(twin.coding_score or 65.0),
            "Aptitude": float(twin.aptitude_score or 65.0),
            "Projects": float(twin.project_score or 60.0),
            "Communication": float(twin.communication_score or 65.0),
            "Logical": float(twin.logical_score or 65.0),
            "Leadership": float(twin.leadership_score or 60.0)
        }
    )

    # 8. Top Action Items (from Recommendations)
    recs = db.query(Recommendation).filter(
        Recommendation.student_profile_id == profile.id,
        Recommendation.is_completed == False,
        Recommendation.is_dismissed == False
    ).order_by(Recommendation.created_at.desc()).limit(3).all()

    action_items = []
    for r in recs:
        action_items.append(DashboardActionItem(
            id=r.id,
            title=r.title,
            category=r.type,
            priority=r.priority or "High",
            action_url=r.action_url
        ))

    if not action_items:
        # Default smart action items
        action_items = [
            DashboardActionItem(title="Resolve top missing critical skills", category="skill", priority="High", action_url="/skill-gap"),
            DashboardActionItem(title="Simulate career trajectory in What-If Sandbox", category="twin", priority="Medium", action_url="/career-twin"),
            DashboardActionItem(title="Complete active milestone in Career Roadmap", category="roadmap", priority="High", action_url="/roadmap")
        ]

    return StudentDashboardResponse(
        profile=prof_summary,
        resume=resume_summary,
        target_job=target_summary,
        skill_gap=gap_summary,
        placement=placement_summary,
        roadmap=roadmap_summary,
        career_twin=twin_summary,
        top_action_items=action_items,
        generated_at=datetime.now(timezone.utc)
    )
