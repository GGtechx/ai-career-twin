"""
Personalized Career Recommendation Service
Synthesizes student profile, skill gap results, placement readiness, target job,
and interests to generate scored recommendations across 7 categories.
Persists recommendations into the recommendations database table.
"""
import logging
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import Course, Recommendation, JobRole, SkillGapResult, PlacementReadiness
from app.models.student_profile import StudentProfile
from app.models.user import User

logger = logging.getLogger("app.services.recommendation_service")

# High-quality, reliable reference documentation for key skills
SKILL_RESOURCE_MAP = {
    "python": "https://docs.python.org/3/tutorial/",
    "fastapi": "https://fastapi.tiangolo.com/tutorial/",
    "react": "https://react.dev/learn",
    "docker": "https://docs.docker.com/get-started/",
    "kubernetes": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
    "postgresql": "https://www.postgresql.org/docs/current/tutorial.html",
    "sql": "https://www.w3schools.com/sql/",
    "javascript": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript",
    "typescript": "https://www.typescriptlang.org/docs/handbook/intro.html",
    "aws": "https://aws.amazon.com/getting-started/hands-on/",
    "git": "https://git-scm.com/book/en/v2",
    "github": "https://docs.github.com/en/get-started",
    "redis": "https://redis.io/docs/latest/develop/get-started/",
    "mongodb": "https://www.mongodb.com/docs/manual/tutorial/",
    "node": "https://nodejs.org/en/learn",
    "node.js": "https://nodejs.org/en/learn",
    "nodejs": "https://nodejs.org/en/learn",
    "c++": "https://www.learncpp.com/",
    "java": "https://dev.java/learn/",
    "go": "https://go.dev/tour/welcome/1",
    "golang": "https://go.dev/tour/welcome/1",
    "html": "https://developer.mozilla.org/en-US/docs/Learn/HTML",
    "css": "https://developer.mozilla.org/en-US/docs/Learn/CSS",
    "linux": "https://linuxjourney.com/",
    "rest api": "https://restfulapi.net/",
    "restful apis": "https://restfulapi.net/",
    "restful api": "https://restfulapi.net/",
    "microservices": "https://microservices.io/patterns/microservices.html",
    "data structures": "https://www.geeksforgeeks.org/data-structures/",
    "algorithms": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/",
    "machine learning": "https://scikit-learn.org/stable/tutorial/index.html",
    "deep learning": "https://pytorch.org/tutorials/beginner/basics/intro.html",
    "system design": "https://github.com/donnemartin/system-design-primer",
    "spring boot": "https://spring.io/guides/gs/rest-service/",
    "django": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
    "graphql": "https://graphql.org/learn/",
    "kafka": "https://kafka.apache.org/quickstart",
    "ci/cd": "https://www.redhat.com/en/topics/devops/what-is-ci-cd"
}

def resolve_skill_url(skill_name: str) -> str:
    key = skill_name.strip().lower()
    if key in SKILL_RESOURCE_MAP:
        return SKILL_RESOURCE_MAP[key]
    for k, v in SKILL_RESOURCE_MAP.items():
        if k in key or key in k:
            return v
    encoded = urllib.parse.quote_plus(skill_name)
    return f"https://www.geeksforgeeks.org/search/?q={encoded}"

def resolve_project_url(project_title: str) -> str:
    lower = project_title.lower()
    if "microservice" in lower or "caching" in lower or "redis" in lower:
        return "https://github.com/practical-tutorials/project-based-learning#go"
    if "cloud" in lower or "devops" in lower or "docker" in lower:
        return "https://github.com/practical-tutorials/project-based-learning#devops"
    if "machine learning" in lower or "ai" in lower:
        return "https://github.com/practical-tutorials/project-based-learning#machine-learning"
    return "https://github.com/practical-tutorials/project-based-learning#web-development"

def sanitize_action_url(action_url: Optional[str], rec_type: str, title: str, mapped_skills: List[str]) -> str:
    if not action_url or "devdocs.io" in action_url:
        skill = mapped_skills[0] if mapped_skills else title
        return resolve_skill_url(skill)
    if action_url.strip() in ["https://github.com/", "https://github.com", "http://github.com/"]:
        return resolve_project_url(title)
    if "pramp.com" in action_url:
        return "https://www.techinterviewhandbook.org/"
    return action_url

# Sample course library to seed in DB with working, free learning links
SAMPLE_COURSES = [
    {
        "title": "Full-Stack Web Development with React & FastAPI",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/full-stack-developer/",
        "domain": "Web & Backend",
        "difficulty_level": "Intermediate",
        "duration_hours": 36.0,
        "rating": 4.8,
        "is_free": True,
        "mapped_skills": ["React", "FastAPI", "Python", "PostgreSQL", "Docker", "REST API"]
    },
    {
        "title": "Data Structures & Algorithms Deep Dive",
        "provider": "NeetCode",
        "url": "https://neetcode.io/roadmap",
        "domain": "Algorithms & Problem Solving",
        "difficulty_level": "Intermediate",
        "duration_hours": 45.0,
        "rating": 4.9,
        "is_free": True,
        "mapped_skills": ["Data Structures", "Algorithms", "Python", "C++", "Java", "Problem Solving"]
    },
    {
        "title": "Docker, Kubernetes & AWS Cloud DevOps Bootcamp",
        "provider": "Docker / AWS Official",
        "url": "https://docs.docker.com/get-started/",
        "domain": "Cloud & DevOps",
        "difficulty_level": "Intermediate",
        "duration_hours": 28.0,
        "rating": 4.7,
        "is_free": True,
        "mapped_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"]
    },
    {
        "title": "Applied Machine Learning & Deep Learning with PyTorch",
        "provider": "DeepLearning.AI",
        "url": "https://www.deeplearning.ai/courses/",
        "domain": "AI / Machine Learning",
        "difficulty_level": "Advanced",
        "duration_hours": 40.0,
        "rating": 4.9,
        "is_free": True,
        "mapped_skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "Transformers"]
    },
    {
        "title": "Modern Go (Golang) Programming for Distributed Systems",
        "provider": "Go Dev Official",
        "url": "https://go.dev/tour/",
        "domain": "Backend Systems",
        "difficulty_level": "Beginner",
        "duration_hours": 20.0,
        "rating": 4.6,
        "is_free": True,
        "mapped_skills": ["Go", "Microservices", "gRPC", "Docker"]
    },
    {
        "title": "Quantitative Aptitude & Logical Reasoning for Placement Drives",
        "provider": "GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/placements-gq/",
        "domain": "Aptitude",
        "difficulty_level": "Beginner",
        "duration_hours": 25.0,
        "rating": 4.5,
        "is_free": True,
        "mapped_skills": ["Aptitude", "Problem Solving", "Logical Reasoning"]
    }
]


def _seed_courses_if_empty(db: Session):
    """Seeds sample courses into database if none exist."""
    if db.query(Course).count() == 0:
        for c_data in SAMPLE_COURSES:
            course = Course(**c_data)
            db.add(course)
        db.commit()
        logger.info("Sample courses seeded in database.")


def generate_personalized_recommendations(
    db: Session,
    user: User,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Synthesizes student's target job, skill gaps, readiness score, and interests
    to generate prioritized recommendations across 7 categories.
    """
    _seed_courses_if_empty(db)

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found. Please complete profile first.")

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

    missing_critical = list(latest_gap.missing_critical_skills or []) if latest_gap else []
    missing_secondary = list(latest_gap.missing_secondary_skills or []) if latest_gap else []

    target_job_title = (target_job.title if target_job else profile.target_job_role) or "Software Engineer"
    target_company_name = (target_job.company.name if (target_job and target_job.company) else profile.target_company) or "Target Tech Corp"

    interests = [i.lower() for i in (profile.interests or [])]
    coding_score = float(profile.coding_score or 65.0)
    aptitude_score = float(profile.aptitude_score or 65.0)

    # Clear old active recommendations if force_refresh
    if force_refresh:
        db.query(Recommendation).filter(
            Recommendation.student_profile_id == profile.id,
            Recommendation.is_completed == False
        ).delete()
        db.commit()

    recs_to_create: List[Dict[str, Any]] = []

    # ----------------------------------------------------
    # Category 1: Skills to Learn (Priority Gaps)
    # ----------------------------------------------------
    for skill in missing_critical[:3]:
        recs_to_create.append({
            "type": "skill",
            "title": f"Master {skill} (Critical Job Requirement)",
            "description": f"Essential skill for {target_job_title} at {target_company_name}. Focus on building end-to-end functionality using {skill}.",
            "priority": "High",
            "action_url": resolve_skill_url(skill),
            "relevance_score": 95.0,
            "mapped_skills": [skill]
        })

    for skill in missing_secondary[:2]:
        recs_to_create.append({
            "type": "skill",
            "title": f"Learn {skill} (Competitive Advantage)",
            "description": f"Preferred bonus skill for {target_job_title}. Differentiates you from peer applicants.",
            "priority": "Medium",
            "action_url": resolve_skill_url(skill),
            "relevance_score": 75.0,
            "mapped_skills": [skill]
        })

    # ----------------------------------------------------
    # Category 2: Online Courses
    # ----------------------------------------------------
    courses = db.query(Course).all()
    all_missing = set(s.lower() for s in (missing_critical + missing_secondary))
    for c in courses:
        mapped = [m.lower() for m in (c.mapped_skills or [])]
        overlap = set(mapped).intersection(all_missing)
        if overlap or any(i in c.domain.lower() for i in interests):
            recs_to_create.append({
                "type": "course",
                "title": c.title,
                "description": f"Comprehensive {c.difficulty_level} course ({c.duration_hours or 30}h) covering {', '.join(c.mapped_skills[:4])}.",
                "priority": "High" if overlap else "Medium",
                "action_url": c.url,
                "course_id": c.id,
                "course_provider": c.provider,
                "relevance_score": 90.0 if overlap else 70.0,
                "mapped_skills": c.mapped_skills
            })

    # ----------------------------------------------------
    # Category 3: Recommended Projects
    # ----------------------------------------------------
    top_missing_str = ", ".join(missing_critical[:2]) if missing_critical else "React and FastAPI"
    recs_to_create.append({
        "type": "project",
        "title": f"Build a {target_job_title} Capstone Platform",
        "description": f"Develop an end-to-end cloud-deployed application integrating {top_missing_str}. Implement authentication, RESTful APIs, and responsive UI.",
        "priority": "High",
        "action_url": resolve_project_url(target_job_title),
        "relevance_score": 88.0,
        "mapped_skills": missing_critical[:3] or ["Full Stack", "APIs", "Database"]
    })

    recs_to_create.append({
        "type": "project",
        "title": "Microservices & Distributed Caching Service",
        "description": "Architect high-throughput microservices using Docker containers, Redis in-memory caching, and asynchronous workers.",
        "priority": "Medium",
        "action_url": "https://github.com/practical-tutorials/project-based-learning#go",
        "relevance_score": 78.0,
        "mapped_skills": ["Docker", "Redis", "Microservices", "REST API"]
    })

    # ----------------------------------------------------
    # Category 4: Certifications
    # ----------------------------------------------------
    recs_to_create.append({
        "type": "certification",
        "title": "AWS Certified Cloud Practitioner or Azure Fundamentals",
        "description": f"Validates cloud infrastructure competencies highly valued by {target_company_name}.",
        "priority": "High" if "cloud" in target_job_title.lower() or "aws" in all_missing else "Medium",
        "action_url": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
        "relevance_score": 82.0,
        "mapped_skills": ["AWS", "Cloud Computing"]
    })

    # ----------------------------------------------------
    # Category 5: Coding Practice
    # ----------------------------------------------------
    coding_priority = "High" if coding_score < 70 else "Medium"
    recs_to_create.append({
        "type": "coding",
        "title": f"Solve {target_company_name} Top 50 DSA Problems",
        "description": f"Targeted problem set focusing on HashMaps, Dynamic Programming, Graphs, and Binary Trees. Current score: {coding_score:.1f}/100.",
        "priority": coding_priority,
        "action_url": "https://neetcode.io/practice",
        "relevance_score": 85.0 if coding_score < 70 else 68.0,
        "mapped_skills": ["Data Structures", "Algorithms", "Coding"]
    })

    # ----------------------------------------------------
    # Category 6: Aptitude Preparation
    # ----------------------------------------------------
    apt_priority = "High" if aptitude_score < 70 else "Low"
    recs_to_create.append({
        "type": "aptitude",
        "title": "Speed Math, Probability & Quantitative Aptitude Sets",
        "description": "Daily 30-minute timed mock tests for quantitative aptitude, permutations, work & time, and syllogisms.",
        "priority": apt_priority,
        "action_url": "https://www.geeksforgeeks.org/aptitude-questions-and-answers/",
        "relevance_score": 80.0 if aptitude_score < 70 else 55.0,
        "mapped_skills": ["Aptitude", "Quantitative"]
    })

    # ----------------------------------------------------
    # Category 7: Interview Preparation
    # ----------------------------------------------------
    recs_to_create.append({
        "type": "interview",
        "title": f"{target_company_name} Technical & System Design Mock Interview",
        "description": f"Prepare STAR method behavioral responses and high-level architectural walkthroughs tailored for {target_company_name}.",
        "priority": "High",
        "action_url": "https://www.techinterviewhandbook.org/",
        "relevance_score": 86.0,
        "mapped_skills": ["Communication", "System Design", "Behavioral Interview"]
    })

    # Persist into DB
    saved_items: List[Dict[str, Any]] = []
    for r_data in recs_to_create:
        # Check if already exists for student
        existing = db.query(Recommendation).filter(
            Recommendation.student_profile_id == profile.id,
            Recommendation.title == r_data["title"]
        ).first()

        if not existing:
            rec = Recommendation(
                student_profile_id=profile.id,
                course_id=r_data.get("course_id"),
                type=r_data["type"],
                title=r_data["title"],
                description=r_data["description"],
                priority=r_data["priority"],
                action_url=r_data.get("action_url")
            )
            db.add(rec)
            db.flush()
            rec_id = rec.id
            is_comp = False
            is_dism = False
            created_at = rec.created_at
        else:
            rec_id = existing.id
            is_comp = existing.is_completed
            is_dism = existing.is_dismissed
            created_at = existing.created_at
            # Update action_url on existing records to ensure active, working links
            if r_data.get("action_url"):
                existing.action_url = r_data.get("action_url")

        saved_items.append({
            "id": rec_id,
            "type": r_data["type"],
            "title": r_data["title"],
            "description": r_data["description"],
            "priority": r_data["priority"],
            "action_url": r_data.get("action_url"),
            "course_id": r_data.get("course_id"),
            "course_provider": r_data.get("course_provider"),
            "mapped_skills": r_data.get("mapped_skills", []),
            "relevance_score": r_data.get("relevance_score", 75.0),
            "is_completed": is_comp,
            "is_dismissed": is_dism,
            "created_at": created_at or datetime.utcnow()
        })

    db.commit()

    # Group by category
    by_category: Dict[str, List[Dict[str, Any]]] = {
        "skill": [],
        "course": [],
        "project": [],
        "certification": [],
        "coding": [],
        "aptitude": [],
        "interview": []
    }

    for item in saved_items:
        t = item["type"]
        if t in by_category:
            by_category[t].append(item)

    high_pri = len([i for i in saved_items if i["priority"] == "High"])

    return {
        "student_profile_id": profile.id,
        "target_job_title": target_job_title,
        "target_company_name": target_company_name,
        "total_recommendations": len(saved_items),
        "by_category": by_category,
        "high_priority_count": high_pri,
        "generated_at": datetime.utcnow()
    }


def get_student_recommendations(
    db: Session,
    user: User
) -> Dict[str, Any]:
    """Retrieves existing recommendations or generates fresh ones."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Profile not found.")

    count = db.query(Recommendation).filter(Recommendation.student_profile_id == profile.id).count()
    if count == 0:
        return generate_personalized_recommendations(db, user)

    # Check if existing recommendations correspond to the active target company
    target_comp = profile.target_company
    if target_comp:
        interview_rec = db.query(Recommendation).filter(
            Recommendation.student_profile_id == profile.id,
            Recommendation.type == "interview"
        ).first()
        if interview_rec and target_comp.lower() not in (interview_rec.title or "").lower():
            # Target company changed! Auto-refresh recommendations to avoid stale data
            return generate_personalized_recommendations(db, user, force_refresh=True)

    # Fetch and categorize existing recommendations
    recs = db.query(Recommendation).filter(
        Recommendation.student_profile_id == profile.id,
        Recommendation.is_dismissed == False
    ).order_by(Recommendation.priority.asc(), Recommendation.created_at.desc()).all()

    by_category: Dict[str, List[Dict[str, Any]]] = {
        "skill": [],
        "course": [],
        "project": [],
        "certification": [],
        "coding": [],
        "aptitude": [],
        "interview": []
    }

    high_pri = 0
    needs_commit = False
    for r in recs:
        # Sanitize any legacy broken URLs (devdocs.io, raw github, etc.) in existing DB records
        skills = r.course.mapped_skills if r.course else []
        cleaned_url = sanitize_action_url(r.action_url, r.type, r.title, skills)
        if cleaned_url != r.action_url:
            r.action_url = cleaned_url
            needs_commit = True

        if r.priority == "High":
            high_pri += 1
        item = {
            "id": r.id,
            "type": r.type,
            "title": r.title,
            "description": r.description,
            "priority": r.priority,
            "action_url": cleaned_url,
            "course_id": r.course_id,
            "course_provider": r.course.provider if r.course else None,
            "mapped_skills": skills,
            "relevance_score": 85.0 if r.priority == "High" else 65.0,
            "is_completed": r.is_completed,
            "is_dismissed": r.is_dismissed,
            "created_at": r.created_at
        }
        if r.type in by_category:
            by_category[r.type].append(item)

    if needs_commit:
        db.commit()

    return {
        "student_profile_id": profile.id,
        "target_job_title": profile.target_job_role or "Software Engineer",
        "target_company_name": profile.target_company or "Target Tech Corp",
        "total_recommendations": len(recs),
        "by_category": by_category,
        "high_priority_count": high_pri,
        "generated_at": datetime.utcnow()
    }


def update_recommendation_status(
    db: Session,
    user: User,
    recommendation_id: int,
    is_completed: Optional[bool] = None,
    is_dismissed: Optional[bool] = None
) -> Dict[str, Any]:
    """Updates completion or dismissed status of a recommendation item."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Profile not found.")

    rec = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.student_profile_id == profile.id
    ).first()

    if not rec:
        raise ValueError(f"Recommendation with ID {recommendation_id} not found.")

    if is_completed is not None:
        rec.is_completed = is_completed
    if is_dismissed is not None:
        rec.is_dismissed = is_dismissed

    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "is_completed": rec.is_completed, "is_dismissed": rec.is_dismissed}
