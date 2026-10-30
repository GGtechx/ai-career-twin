"""
Skill Gap Analysis Service
Compares student skills against target company job requirements using
NLP skill normalization, keyword matching, and TF-IDF cosine similarity.
Stores results in the skill_gap_results database table.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.models import JobRole, JobRequirement, SkillGapResult
from app.models.student_profile import StudentProfile
from app.models.user import User

logger = logging.getLogger("app.services.skill_gap_service")

# Canonical mapping for normalizing skill variations
SYNONYM_MAP = {
    "react.js": "React",
    "reactjs": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "k8s": "Kubernetes",
    "aws lambda": "AWS",
    "amazon web services": "AWS",
    "azure cloud": "Azure",
    "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "fast api": "FastAPI",
    "django rest framework": "Django",
    "drf": "Django",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "golang": "Go",
    "ts": "TypeScript",
    "js": "JavaScript",
    "py": "Python",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "tf": "TensorFlow",
    "rest": "REST API",
    "restful": "REST API",
    "rest api": "REST API",
    "dsa": "Data Structures & Algorithms",
    "data structures": "Data Structures",
    "algorithms": "Algorithms"
}

def normalize_skill(skill_name: str) -> str:
    """Normalizes skill string to canonical form."""
    clean = skill_name.strip().lower()
    if clean in SYNONYM_MAP:
        return SYNONYM_MAP[clean]
    for syn, canonical in SYNONYM_MAP.items():
        if syn == clean:
            return canonical
    return skill_name.strip().title()


def _semantic_skill_match(student_skill_list: List[str], required_skill: str) -> Tuple[bool, Optional[str], float]:
    """
    Checks if required_skill is present in student_skill_list.
    Returns (is_match, matched_student_skill, similarity_score).
    Uses exact normalized comparison first, then TF-IDF cosine similarity.
    """
    norm_req = normalize_skill(required_skill).lower()

    # 1. Exact normalized check
    for s in student_skill_list:
        if normalize_skill(s).lower() == norm_req or s.strip().lower() == required_skill.strip().lower():
            return True, s, 1.0

    # 2. Substring check
    for s in student_skill_list:
        s_norm = normalize_skill(s).lower()
        if (len(s_norm) >= 4 and s_norm in norm_req) or (len(norm_req) >= 4 and norm_req in s_norm):
            return True, s, 0.88

    # 3. TF-IDF Cosine Similarity for multi-word or fuzzy terms
    try:
        corpus = [required_skill] + student_skill_list
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        max_idx = sim_scores.argmax()
        if sim_scores[max_idx] >= 0.72:
            return True, student_skill_list[max_idx], float(sim_scores[max_idx])
    except Exception as e:
        logger.debug(f"TF-IDF comparison fallback: {e}")

    return False, None, 0.0


def analyze_skill_gap(
    db: Session,
    user: User,
    job_role_id: int
) -> Dict[str, Any]:
    """
    Performs comprehensive Skill Gap Analysis for the authenticated student
    against the specified target JobRole.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found. Please complete profile first.")

    job = db.query(JobRole).filter(JobRole.id == job_role_id).first()
    if not job:
        raise ValueError(f"Job role with ID {job_role_id} not found.")

    req = job.job_requirement
    if not req:
        raise ValueError(f"No requirement specification found for job '{job.title}'.")

    # Combine student skills from profile and parsed resume if available
    profile_tech = list(profile.technical_skills or [])
    profile_langs = list(profile.programming_languages or [])
    profile_soft = list(profile.soft_skills or [])

    # Check latest resume skills if present
    latest_resume = profile.resumes[-1] if profile.resumes else None
    resume_skills = []
    if latest_resume and latest_resume.extracted_skills:
        resume_skills = (
            latest_resume.extracted_skills.get("technical_skills", []) +
            latest_resume.extracted_skills.get("programming_languages", [])
        )

    all_student_skills = list(dict.fromkeys(profile_tech + profile_langs + resume_skills))

    must_have = req.must_have_skills or []
    good_to_have = req.good_to_have_skills or []

    # Match calculation
    matched_skills = []
    missing_critical = []
    missing_secondary = []
    priority_skill_gaps = []

    # Check Must-Have Skills (Critical)
    for skill in must_have:
        matched, student_skill, score = _semantic_skill_match(all_student_skills, skill)
        if matched:
            matched_skills.append(skill)
        else:
            missing_critical.append(skill)
            priority_skill_gaps.append({
                "skill": skill,
                "priority": "High Priority",
                "category": "Must-Have",
                "recommendation": f"Core requirement for {job.title}. Focus on hands-on project implementations and foundational concepts in {skill}."
            })

    # Check Good-To-Have Skills (Secondary)
    for skill in good_to_have:
        matched, student_skill, score = _semantic_skill_match(all_student_skills, skill)
        if matched:
            if skill not in matched_skills:
                matched_skills.append(skill)
        else:
            missing_secondary.append(skill)
            priority_skill_gaps.append({
                "skill": skill,
                "priority": "Medium Priority",
                "category": "Preferred",
                "recommendation": f"Competitive advantage skill. Recommended online course or certification in {skill}."
            })

    # Calculate overall match percentage
    must_have_weight = 70.0
    good_to_have_weight = 30.0

    must_count = max(len(must_have), 1)
    good_count = max(len(good_to_have), 1)

    matched_must = len([s for s in must_have if s in matched_skills])
    matched_good = len([s for s in good_to_have if s in matched_skills])

    pct_must = (matched_must / must_count) * must_have_weight
    pct_good = (matched_good / good_count) * good_to_have_weight
    match_percentage = round(pct_must + pct_good, 1)

    # Determine readiness tier
    if match_percentage >= 75.0:
        readiness_tier = "High Readiness"
    elif match_percentage >= 50.0:
        readiness_tier = "Moderate Readiness"
    else:
        readiness_tier = "Low Readiness"

    # Skill strengths (skills student possesses that align directly with target job)
    skill_strengths = list(dict.fromkeys(matched_skills))

    # Recommended skills to learn (top 5 missing)
    recommended_skills = list(dict.fromkeys(missing_critical + missing_secondary))[:6]

    # Academic & Profile Eligibility Check
    student_cgpa = float(profile.cgpa or 0.0)
    cgpa_eligible = student_cgpa >= req.min_cgpa
    branch_eligible = (
        not req.eligible_branches or
        (profile.branch and any(b.lower() in profile.branch.lower() for b in req.eligible_branches))
    )
    backlogs_eligible = (profile.academic_record.active_backlogs <= req.max_active_backlogs) if profile.academic_record else True

    eligibility_status = {
        "overall_eligible": bool(cgpa_eligible and branch_eligible and backlogs_eligible),
        "cgpa": {"student": student_cgpa, "required": req.min_cgpa, "eligible": cgpa_eligible},
        "branch": {"student": profile.branch or "Not set", "allowed": req.eligible_branches, "eligible": branch_eligible},
        "backlogs": {"allowed_max": req.max_active_backlogs, "eligible": backlogs_eligible}
    }

    # Analysis notes
    notes = (
        f"Evaluated {len(all_student_skills)} candidate skills against {len(must_have)} critical and "
        f"{len(good_to_have)} preferred requirements for {job.title} at {job.company.name if job.company else 'target company'}. "
        f"Match: {match_percentage}%. Tier: {readiness_tier}."
    )

    # Save or update result in database
    existing_result = db.query(SkillGapResult).filter(
        SkillGapResult.student_profile_id == profile.id,
        SkillGapResult.job_role_id == job.id
    ).first()

    if existing_result:
        existing_result.match_percentage = match_percentage
        existing_result.matching_skills = matched_skills
        existing_result.missing_critical_skills = missing_critical
        existing_result.missing_secondary_skills = missing_secondary
        existing_result.readiness_tier = readiness_tier
        existing_result.analysis_notes = notes
        skill_gap_record = existing_result
    else:
        skill_gap_record = SkillGapResult(
            student_profile_id=profile.id,
            job_role_id=job.id,
            match_percentage=match_percentage,
            matching_skills=matched_skills,
            missing_critical_skills=missing_critical,
            missing_secondary_skills=missing_secondary,
            readiness_tier=readiness_tier,
            analysis_notes=notes
        )
        db.add(skill_gap_record)

    db.commit()
    db.refresh(skill_gap_record)

    return {
        "id": skill_gap_record.id,
        "student_profile_id": profile.id,
        "job_role_id": job.id,
        "job_title": job.title,
        "company_name": job.company.name if job.company else "Target Company",
        "match_percentage": match_percentage,
        "readiness_tier": readiness_tier,
        "matched_skills": matched_skills,
        "missing_critical_skills": missing_critical,
        "missing_secondary_skills": missing_secondary,
        "priority_skill_gaps": priority_skill_gaps,
        "skill_strengths": skill_strengths,
        "recommended_skills": recommended_skills,
        "eligibility_status": eligibility_status,
        "analysis_notes": notes,
        "created_at": skill_gap_record.created_at
    }


def get_latest_skill_gap_result(
    db: Session,
    user: User,
    job_role_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Retrieves the most recent skill gap evaluation for the student, aligned with active target."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        return None

    target_job_id = job_role_id
    if not target_job_id and profile.target_job_role:
        from app.models.models import JobRole, Company
        job_query = db.query(JobRole)
        if profile.target_company:
            job = job_query.join(Company).filter(
                JobRole.title == profile.target_job_role,
                Company.name == profile.target_company
            ).first()
        else:
            job = None
        if not job:
            job = db.query(JobRole).filter(JobRole.title == profile.target_job_role).first()
        if job:
            target_job_id = job.id

    query = db.query(SkillGapResult).filter(SkillGapResult.student_profile_id == profile.id)
    if target_job_id:
        query = query.filter(SkillGapResult.job_role_id == target_job_id)
    
    result = query.order_by(SkillGapResult.created_at.desc()).first()
    if not result and target_job_id:
        # Auto-run analysis for target job if none exists
        try:
            return analyze_skill_gap(db, user, target_job_id)
        except Exception:
            return None

    if not result:
        return None

    job = result.job_role
    return {
        "id": result.id,
        "student_profile_id": result.student_profile_id,
        "job_role_id": result.job_role_id,
        "job_title": job.title if job else "Target Job",
        "company_name": job.company.name if job and job.company else "Target Company",
        "match_percentage": result.match_percentage,
        "readiness_tier": result.readiness_tier,
        "matched_skills": result.matching_skills or [],
        "missing_critical_skills": result.missing_critical_skills or [],
        "missing_secondary_skills": result.missing_secondary_skills or [],
        "priority_skill_gaps": [
            {
                "skill": s,
                "priority": "High Priority",
                "category": "Must-Have",
                "recommendation": f"Core competency for {job.title if job else 'this role'}."
            } for s in (result.missing_critical_skills or [])
        ],
        "skill_strengths": result.matching_skills or [],
        "recommended_skills": (result.missing_critical_skills or [])[:5],
        "eligibility_status": {"overall_eligible": True},
        "analysis_notes": result.analysis_notes,
        "created_at": result.created_at
    }
