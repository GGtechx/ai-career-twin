import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.models import (
    DigitalCareerTwin, SkillGapResult, PlacementReadiness,
    CareerRoadmap, JobRole, Company, ProgressTracking
)
from app.services.skill_gap_service import analyze_skill_gap
from app.services.placement_service import predict_placement_readiness

logger = logging.getLogger("app.services.career_twin_service")


def _calculate_benchmark_percentile(score: float) -> float:
    """Calculates percentile ranking based on standard academic distribution."""
    # Sigmoidal mapping centered at 68.0 with stddev ~12.0
    import math
    z = (score - 68.0) / 12.0
    percentile = 1.0 / (1.0 + math.exp(-1.6 * z)) * 100.0
    return round(max(5.0, min(99.0, percentile)), 1)


def get_or_create_twin(db: Session, user: User) -> DigitalCareerTwin:
    """Retrieves existing Digital Career Twin or creates initial instance."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found.")

    twin = db.query(DigitalCareerTwin).filter(
        DigitalCareerTwin.student_profile_id == profile.id
    ).first()

    if not twin:
        student_name = getattr(user, "full_name", None) or "Student"
        twin = DigitalCareerTwin(
            student_profile_id=profile.id,
            twin_name=f"{student_name}'s Career Twin",
            twin_version=1,
            coding_score=float(profile.coding_score or 65.0),
            aptitude_score=float(profile.aptitude_score or 65.0),
            communication_score=float(profile.communication_score or 65.0),
            logical_score=float(profile.aptitude_score or 65.0),
            leadership_score=60.0,
            project_score=50.0 + min(len(profile.projects or []) * 15.0, 45.0),
            overall_twin_score=64.0,
            benchmark_percentile=50.0,
            projected_placement_chance=60.0,
            projected_salary_lpa=7.5,
            radar_history=[],
            simulation_state={}
        )
        db.add(twin)
        db.commit()
        db.refresh(twin)

    return twin


def sync_career_twin(
    db: Session,
    user: User,
    trigger_event: Optional[str] = None
) -> Dict[str, Any]:
    """
    Core Update Engine:
    Recalculates all multidimensional Career Twin scores, updates benchmark percentile,
    appends timeline event, and persists state into PostgreSQL/SQLite.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found.")

    twin = get_or_create_twin(db, user)

    # 1. Fetch latest dependent module outputs aligned with active target job
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

    roadmap_query = db.query(CareerRoadmap).filter(
        CareerRoadmap.student_profile_id == profile.id,
        CareerRoadmap.status == "Active"
    )
    if target_job:
        active_roadmap = roadmap_query.filter(CareerRoadmap.job_role_id == target_job.id).order_by(CareerRoadmap.created_at.desc()).first()
        if not active_roadmap:
            active_roadmap = roadmap_query.order_by(CareerRoadmap.created_at.desc()).first()
    else:
        active_roadmap = roadmap_query.order_by(CareerRoadmap.created_at.desc()).first()

    # 2. Derive multi-dimensional radar scores (0 to 100)
    coding_score = float(profile.coding_score or 65.0)
    aptitude_score = float(profile.aptitude_score or 65.0)
    comm_score = float(profile.communication_score or 65.0)

    # Logical score derived from aptitude & problem solving
    logical_score = round(aptitude_score * 0.7 + coding_score * 0.3, 1)

    # Project score derived from count and tech stack diversity
    projects_count = len(profile.projects or [])
    project_score = round(min(98.0, 50.0 + (projects_count * 15.0) + (10.0 if projects_count >= 2 else 0.0)), 1)

    # Leadership score derived from internships and soft skills
    internships_count = len(profile.internships or [])
    leadership_score = round(min(95.0, 55.0 + (internships_count * 15.0) + min(len(profile.soft_skills or []) * 5.0, 15.0)), 1)

    # Weighted Overall Twin Score
    overall_twin_score = round(
        (coding_score * 0.25) +
        (aptitude_score * 0.20) +
        (project_score * 0.20) +
        (comm_score * 0.15) +
        (logical_score * 0.10) +
        (leadership_score * 0.10),
        1
    )

    percentile = _calculate_benchmark_percentile(overall_twin_score)

    placement_chance = float(latest_readiness.placement_probability * 100.0) if latest_readiness else 65.0
    salary_est = float(latest_readiness.predicted_salary_min_lpa or 7.5) if latest_readiness else 7.5

    # Roadmap progress & stage
    stage_name = "Skill Foundation"
    roadmap_pct = 0.0
    if active_roadmap:
        total = max(active_roadmap.total_milestones or 1, 1)
        completed = active_roadmap.completed_milestones or 0
        roadmap_pct = round((completed / total) * 100.0, 1)
        if active_roadmap.roadmap_data:
            for s in active_roadmap.roadmap_data:
                if any(i.get("status") != "Completed" for i in s.get("items", [])):
                    stage_name = s.get("stage_name", "Skill Foundation")
                    break

    # 3. Update twin model fields
    twin.twin_version = (twin.twin_version or 1) + 1
    twin.coding_score = coding_score
    twin.aptitude_score = aptitude_score
    twin.communication_score = comm_score
    twin.logical_score = logical_score
    twin.project_score = project_score
    twin.leadership_score = leadership_score
    twin.overall_twin_score = overall_twin_score
    twin.benchmark_percentile = percentile
    twin.projected_placement_chance = round(placement_chance, 1)
    twin.projected_salary_lpa = round(salary_est, 1)

    # 4. Construct event history / timeline
    existing_history = list(twin.radar_history or [])
    if trigger_event:
        existing_history.append({
            "event": trigger_event,
            "overall_score": overall_twin_score,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        twin.radar_history = existing_history[-15:]  # Keep last 15 milestone events
        flag_modified(twin, "radar_history")

    db.commit()
    db.refresh(twin)

    # Fetch progress tracking events for comprehensive timeline
    recent_tracking = db.query(ProgressTracking).filter(
        ProgressTracking.student_profile_id == profile.id
    ).order_by(ProgressTracking.created_at.desc()).limit(8).all()

    timeline_items = []
    for t in recent_tracking:
        timeline_items.append({
            "title": t.item_title,
            "category": t.category,
            "status": t.status,
            "date": t.logged_date.isoformat() if t.logged_date else str(t.created_at)
        })

    if not timeline_items and trigger_event:
        timeline_items.append({
            "title": trigger_event,
            "category": "Career Twin Update",
            "status": "Completed",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
        })

    return {
        "id": twin.id,
        "student_profile_id": profile.id,
        "twin_name": twin.twin_name,
        "twin_version": twin.twin_version,
        "coding_score": twin.coding_score,
        "aptitude_score": twin.aptitude_score,
        "communication_score": twin.communication_score,
        "logical_score": twin.logical_score,
        "leadership_score": twin.leadership_score,
        "project_score": twin.project_score,
        "overall_twin_score": twin.overall_twin_score,
        "benchmark_percentile": twin.benchmark_percentile,
        "projected_placement_chance": twin.projected_placement_chance,
        "projected_salary_lpa": twin.projected_salary_lpa,
        "target_company": profile.target_company,
        "target_role": profile.target_job_role,
        "skill_match_percentage": float(latest_gap.match_percentage) if latest_gap else 60.0,
        "placement_readiness_score": float(latest_readiness.readiness_score) if latest_readiness else 65.0,
        "current_roadmap_stage": stage_name,
        "roadmap_progress_percentage": roadmap_pct,
        "radar_breakdown": {
            "Coding": twin.coding_score,
            "Aptitude": twin.aptitude_score,
            "Projects": twin.project_score,
            "Communication": twin.communication_score,
            "Logical": twin.logical_score,
            "Leadership": twin.leadership_score
        },
        "timeline": timeline_items,
        "last_simulated_at": twin.last_simulated_at,
        "created_at": twin.created_at
    }


def simulate_what_if_career_state(
    db: Session,
    user: User,
    req_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    What-If Career Simulation Engine:
    Evaluates simulated gains from adding skills, projects, certifications,
    or improving coding/aptitude scores without modifying permanent student records.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found.")

    twin = get_or_create_twin(db, user)

    # 1. Baseline metrics
    latest_gap = db.query(SkillGapResult).filter(
        SkillGapResult.student_profile_id == profile.id
    ).order_by(SkillGapResult.created_at.desc()).first()

    latest_readiness = db.query(PlacementReadiness).filter(
        PlacementReadiness.student_profile_id == profile.id
    ).order_by(PlacementReadiness.assessed_at.desc()).first()

    base_match = float(latest_gap.match_percentage) if latest_gap else 60.0
    base_readiness = float(latest_readiness.readiness_score) if latest_readiness else 62.0
    base_chance = float(latest_readiness.placement_probability * 100.0) if latest_readiness else 65.0
    base_salary = float(latest_readiness.predicted_salary_min_lpa or 7.5) if latest_readiness else 7.5
    base_twin_score = float(twin.overall_twin_score or 65.0)

    # 2. Extract simulation inputs
    added_skills = [s.strip() for s in req_data.get("added_skills", []) if s.strip()]
    added_projects_count = int(req_data.get("added_projects_count", 0))
    added_certifications = req_data.get("added_certifications", [])
    coding_delta = float(req_data.get("coding_score_delta", 0.0))
    aptitude_delta = float(req_data.get("aptitude_score_delta", 0.0))
    added_internships = int(req_data.get("added_internships_count", 0))

    # 3. Simulate Skill Match against target job
    existing_skills = list(profile.technical_skills or [])
    sim_skills = list(set(existing_skills + added_skills))

    resolved_skills = []
    remaining_gaps = []
    sim_match = base_match

    # Find target job requirements
    job = None
    if profile.target_job_role:
        job = db.query(JobRole).filter(JobRole.title == profile.target_job_role).first()

    if job and job.job_requirement:
        req = job.job_requirement
        must_haves = list(req.must_have_skills or [])
        good_haves = list(req.good_to_have_skills or [])

        # Check which missing skills are newly covered
        for skill in added_skills:
            if any(skill.lower() in m.lower() for m in must_haves + good_haves):
                resolved_skills.append(skill)

        # Estimate new match percentage
        total_req_count = max(len(must_haves) + (len(good_haves) * 0.5), 1)
        sim_matched_count = 0
        for m in must_haves:
            if any(s.lower() in m.lower() or m.lower() in s.lower() for s in sim_skills):
                sim_matched_count += 1
            else:
                remaining_gaps.append(m)

        for g in good_haves:
            if any(s.lower() in g.lower() or g.lower() in s.lower() for s in sim_skills):
                sim_matched_count += 0.5
            else:
                remaining_gaps.append(g)

        sim_match = round(min(100.0, (sim_matched_count / total_req_count) * 100.0), 1)
    else:
        # Fallback simulation formula
        sim_match = round(min(100.0, base_match + (len(added_skills) * 8.5)), 1)
        resolved_skills = added_skills

    # 4. Simulate Placement Readiness & Twin Score
    sim_coding = min(100.0, float(profile.coding_score or 65.0) + coding_delta)
    sim_aptitude = min(100.0, float(profile.aptitude_score or 65.0) + aptitude_delta)
    sim_projects = len(profile.projects or []) + added_projects_count
    sim_internships = len(profile.internships or []) + added_internships

    # Estimate placement score increase based on Random Forest feature importances
    # (Coding ~16%, Aptitude ~15%, Projects & Internships)
    readiness_lift = (coding_delta * 0.22) + (aptitude_delta * 0.20) + (added_projects_count * 4.0) + (added_internships * 6.5) + (len(resolved_skills) * 2.5)
    sim_readiness = round(min(98.0, base_readiness + readiness_lift), 1)
    sim_chance = round(min(99.0, base_chance + (readiness_lift * 1.1)), 1)
    sim_salary = round(base_salary + (readiness_lift * 0.12) + (len(resolved_skills) * 0.3), 1)

    sim_twin_score = round(
        (sim_coding * 0.25) +
        (sim_aptitude * 0.20) +
        (min(98.0, 50.0 + sim_projects * 15.0) * 0.20) +
        (float(profile.communication_score or 65.0) * 0.15) +
        (round(sim_aptitude * 0.7 + sim_coding * 0.3, 1) * 0.10) +
        (min(95.0, 55.0 + sim_internships * 15.0) * 0.10),
        1
    )

    # Update twin's last_simulated_at timestamp
    twin.last_simulated_at = datetime.now(timezone.utc)
    db.commit()

    summary_text = (
        f"Simulating +{len(added_skills)} skill(s), +{added_projects_count} project(s), "
        f"and +{coding_delta:.0f} coding points increases your skill match by +{sim_match - base_match:.1f}% "
        f"and projects your placement readiness from {base_readiness:.1f}% to {sim_readiness:.1f}% "
        f"(+{sim_readiness - base_readiness:.1f}%)."
    )

    return {
        "is_simulation": True,
        "disclaimer": "Simulation results are predictive estimates. They do not alter your permanent career profile.",
        "baseline": {
            "skill_match_percentage": base_match,
            "placement_readiness_score": base_readiness,
            "projected_placement_chance": base_chance,
            "projected_salary_lpa": base_salary,
            "overall_twin_score": base_twin_score
        },
        "simulated": {
            "skill_match_percentage": sim_match,
            "placement_readiness_score": sim_readiness,
            "projected_placement_chance": sim_chance,
            "projected_salary_lpa": sim_salary,
            "overall_twin_score": sim_twin_score
        },
        "deltas": {
            "match_percentage_delta": round(sim_match - base_match, 1),
            "placement_readiness_delta": round(sim_readiness - base_readiness, 1),
            "placement_chance_delta": round(sim_chance - base_chance, 1),
            "salary_delta_lpa": round(sim_salary - base_salary, 1),
            "twin_score_delta": round(sim_twin_score - base_twin_score, 1)
        },
        "resolved_skills": resolved_skills,
        "remaining_skill_gaps": remaining_gaps,
        "analysis_summary": summary_text,
        "simulated_at": datetime.now(timezone.utc)
    }


def on_profile_or_activity_updated(
    db: Session,
    user: User,
    event_label: str
):
    """
    Automatic Career Twin Update Engine hook:
    When a student modifies skills, projects, certifications, internships,
    scores, CGPA, target job, or completes roadmap tasks, this triggers
    recalculation of skill gaps, placement readiness, and career twin sync.
    """
    try:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        if not profile:
            return

        # 1. Recalculate skill gap if target job role is set
        if profile.target_job_role:
            job = db.query(JobRole).filter(JobRole.title == profile.target_job_role).first()
            if job:
                analyze_skill_gap(db, user, job.id)

        # 2. Recalculate placement readiness
        predict_placement_readiness(db, user)

        # 3. Synchronize Career Twin with event label
        sync_career_twin(db, user, trigger_event=event_label)
    except Exception as e:
        logger.warning(f"Background twin auto-update warning: {e}")

