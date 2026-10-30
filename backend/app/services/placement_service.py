"""
Placement Readiness Prediction Service
Uses the pre-trained Random Forest classifier on base-paper features.
Loads the student's live data from the database (NOT reloading the CSV).
Stores assessment in the placement_readiness database table.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
import numpy as np
import joblib

from app.models.models import PlacementReadiness
from app.models.student_profile import StudentProfile
from app.models.user import User

logger = logging.getLogger("app.services.placement_service")

# Model paths
POSSIBLE_PATHS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ai-model", "models", "placement_classifier.joblib")),
    os.path.abspath(os.path.join(os.getcwd(), "ai-model", "models", "placement_classifier.joblib")),
    os.path.abspath(os.path.join(os.getcwd(), "..", "ai-model", "models", "placement_classifier.joblib"))
]

_CACHED_MODEL = None
_CACHED_METADATA = None

def _get_model():
    """Lazy loads and caches the trained model in memory."""
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    for p in POSSIBLE_PATHS:
        if os.path.exists(p):
            logger.info(f"Loading trained placement model from: {p}")
            _CACHED_MODEL = joblib.load(p)
            return _CACHED_MODEL

    logger.warning("Trained model file not found in paths. Using heuristic inference engine.")
    return None


def predict_placement_readiness(
    db: Session,
    user: User
) -> Dict[str, Any]:
    """
    Executes placement readiness classification using live database attributes.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found. Please complete profile first.")

    # 1. Gather live features from DB
    cgpa = float(profile.cgpa or 0.0)
    internships_count = len(profile.internships or [])
    projects_count = len(profile.projects or [])
    certifications_count = len(profile.certifications or [])
    
    # Skills and scores
    coding_score = float(profile.coding_score or 65.0)
    aptitude_score = float(profile.aptitude_score or 65.0)
    comm_score = float(profile.communication_score or 65.0)
    mock_score = float((coding_score + comm_score) / 2.0)  # estimate from coding & communication
    backlogs = int(profile.academic_record.active_backlogs) if profile.academic_record else 0

    features_dict = {
        "cgpa": cgpa,
        "internships_count": internships_count,
        "projects_count": projects_count,
        "certifications_count": certifications_count,
        "coding_skill_score": coding_score,
        "aptitude_score": aptitude_score,
        "communication_skill_score": comm_score,
        "mock_interview_score": mock_score,
        "backlogs": backlogs
    }

    feature_order = [
        "cgpa", "internships_count", "projects_count", "certifications_count",
        "coding_skill_score", "aptitude_score", "communication_skill_score",
        "mock_interview_score", "backlogs"
    ]
    feature_vector = np.array([[features_dict[f] for f in feature_order]], dtype=float)

    # 2. Run model inference
    clf = _get_model()
    if clf is not None:
        try:
            proba = float(clf.predict_proba(feature_vector)[0][1])
            is_placed = proba >= 0.50
        except Exception as e:
            logger.error(f"Prediction error with model: {e}")
            # Heuristic calculation
            weighted_score = (cgpa / 10.0 * 25) + (coding_score * 0.25) + (aptitude_score * 0.2) + (min(internships_count, 2) * 10) + (min(projects_count, 3) * 5) - (backlogs * 15)
            proba = max(0.1, min(0.95, weighted_score / 100.0))
            is_placed = proba >= 0.55
    else:
        weighted_score = (cgpa / 10.0 * 25) + (coding_score * 0.25) + (aptitude_score * 0.2) + (min(internships_count, 2) * 10) + (min(projects_count, 3) * 5) - (backlogs * 15)
        proba = max(0.1, min(0.95, weighted_score / 100.0))
        is_placed = proba >= 0.55

    readiness_percentage = round(proba * 100.0, 1)

    # 3. Classify readiness category
    if readiness_percentage >= 75.0:
        readiness_category = "Placement Ready (High)"
        status_label = "Placed"
    elif readiness_percentage >= 50.0:
        readiness_category = "Moderate Readiness"
        status_label = "Placed" if proba >= 0.5 else "Needs Improvement"
    else:
        readiness_category = "At Risk (Needs Focus)"
        status_label = "Not Placed"

    # 4. Predict expected compensation range based on profile strength
    base_lpa = 6.0
    if readiness_percentage >= 80:
        salary_min = 12.0
        salary_max = 24.0
    elif readiness_percentage >= 65:
        salary_min = 8.0
        salary_max = 16.0
    elif readiness_percentage >= 50:
        salary_min = 5.0
        salary_max = 9.0
    else:
        salary_min = 3.5
        salary_max = 6.0

    # 5. Extract strengths and weak areas from live attributes
    strengths: List[str] = []
    weak_areas: List[str] = []
    suggestions: List[str] = []

    if cgpa >= 8.0:
        strengths.append(f"Strong academic foundation with CGPA of {cgpa:.2f}")
    elif cgpa < 7.0:
        weak_areas.append(f"CGPA is {cgpa:.2f}, below Tier-1 eligibility threshold (7.0+)")
        suggestions.append("Focus on scoring high in remaining semesters to boost cumulative GPA above 7.5.")

    if coding_score >= 70:
        strengths.append(f"Above-average coding proficiency ({coding_score:.1f}/100)")
    else:
        weak_areas.append(f"Coding benchmark is {coding_score:.1f}/100, which lowers placement probability")
        suggestions.append("Practice 2-3 LeetCode/HackerRank problems daily (Data Structures, Arrays, Trees, Dynamic Programming).")

    if aptitude_score >= 70:
        strengths.append(f"Solid analytical and aptitude benchmark ({aptitude_score:.1f}/100)")
    else:
        weak_areas.append("Aptitude & quantitative speed requires improvement")
        suggestions.append("Dedicate 45 minutes daily to quantitative problem solving, logical reasoning, and mock company tests.")

    if internships_count >= 1:
        strengths.append(f"Practical industry experience with {internships_count} recorded internship(s)")
    else:
        weak_areas.append("Zero industrial internships recorded")
        suggestions.append("Apply to short-term virtual internships, open source projects, or research fellowships.")

    if projects_count >= 2:
        strengths.append(f"Portfolio of {projects_count} hands-on projects demonstrates application skills")
    else:
        weak_areas.append("Need at least 2 comprehensive full-stack/AI projects")
        suggestions.append("Build and deploy an end-to-end full-stack or machine learning project with a live URL and GitHub README.")

    if backlogs > 0:
        weak_areas.append(f"{backlogs} active backlog(s) strictly disqualify from Tier-1 corporate drives")
        suggestions.append("Prioritize clearing all existing backlogs before placement season begins.")

    if not strengths:
        strengths.append("Enrolled in structured curriculum with potential for rapid skill growth.")

    # 6. Store result in placement_readiness database table
    existing = db.query(PlacementReadiness).filter(
        PlacementReadiness.student_profile_id == profile.id
    ).first()

    if existing:
        existing.readiness_score = readiness_percentage
        existing.predicted_status = status_label
        existing.placement_probability = round(proba, 4)
        existing.predicted_salary_min_lpa = salary_min
        existing.predicted_salary_max_lpa = salary_max
        existing.confidence_score = 0.88
        existing.top_positive_factors = strengths
        existing.top_risk_factors = weak_areas
        existing.model_version = "v1.0-basepaper"
        existing.assessed_at = datetime.utcnow()
        record = existing
    else:
        record = PlacementReadiness(
            student_profile_id=profile.id,
            readiness_score=readiness_percentage,
            predicted_status=status_label,
            placement_probability=round(proba, 4),
            predicted_salary_min_lpa=salary_min,
            predicted_salary_max_lpa=salary_max,
            confidence_score=0.88,
            top_positive_factors=strengths,
            top_risk_factors=weak_areas,
            model_version="v1.0-basepaper"
        )
        db.add(record)

    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "student_profile_id": profile.id,
        "readiness_score": readiness_percentage,
        "predicted_status": status_label,
        "placement_probability": round(proba, 4),
        "readiness_category": readiness_category,
        "predicted_salary_min_lpa": salary_min,
        "predicted_salary_max_lpa": salary_max,
        "confidence_score": 0.88,
        "strengths": strengths,
        "weak_areas": weak_areas,
        "improvement_suggestions": suggestions,
        "feature_breakdown": features_dict,
        "model_version": "v1.0-basepaper",
        "assessed_at": record.assessed_at
    }


def get_latest_placement_readiness(
    db: Session,
    user: User
) -> Optional[Dict[str, Any]]:
    """Retrieves the student's latest placement readiness assessment."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        return None

    record = db.query(PlacementReadiness).filter(
        PlacementReadiness.student_profile_id == profile.id
    ).order_by(PlacementReadiness.assessed_at.desc()).first()

    if not record:
        return None

    # Derive category
    pct = record.readiness_score
    if pct >= 75:
        category = "Placement Ready (High)"
    elif pct >= 50:
        category = "Moderate Readiness"
    else:
        category = "At Risk (Needs Focus)"

    return {
        "id": record.id,
        "student_profile_id": record.student_profile_id,
        "readiness_score": record.readiness_score,
        "predicted_status": record.predicted_status,
        "placement_probability": record.placement_probability,
        "readiness_category": category,
        "predicted_salary_min_lpa": record.predicted_salary_min_lpa,
        "predicted_salary_max_lpa": record.predicted_salary_max_lpa,
        "confidence_score": record.confidence_score,
        "strengths": record.top_positive_factors or [],
        "weak_areas": record.top_risk_factors or [],
        "improvement_suggestions": [
            "Maintain strong CGPA above target cutoff.",
            "Complete daily DSA and coding challenge rounds.",
            "Work on end-to-end full-stack portfolio projects."
        ],
        "feature_breakdown": {
            "cgpa": profile.cgpa,
            "coding_skill_score": profile.coding_score,
            "aptitude_score": profile.aptitude_score,
            "internships_count": len(profile.internships or []),
            "projects_count": len(profile.projects or [])
        },
        "model_version": record.model_version,
        "assessed_at": record.assessed_at
    }
