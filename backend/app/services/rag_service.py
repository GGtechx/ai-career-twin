import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.models import (
    SkillGapResult, PlacementReadiness, CareerRoadmap,
    Resume, Recommendation, ProgressTracking
)
from app.services.vector_store import vector_store
from app.schemas.ai import (
    CareerAssistantResponse, RetrievedKnowledgeChunk, StudentCareerContext,
    LLMPersonalizedRecommendationResponse, NextSkillRecommendation,
    ProjectRecommendation, LearningPriorityItem, InterviewPrepGuide
)

logger = logging.getLogger("app.services.rag_service")


def _get_student_context(db: Session, user: User) -> Dict[str, Any]:
    """Gathers all live career dimensions for the authenticated student."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found.")

    target_role = profile.target_job_role or "Software Engineer"
    target_company = profile.target_company or "Target Tech Company"

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

    current_stage_name = "Skill Foundation"
    if active_roadmap and active_roadmap.roadmap_data:
        for stage in active_roadmap.roadmap_data:
            items = stage.get("items", [])
            if any(i.get("status") in ["In Progress", "Not Started"] for i in items):
                current_stage_name = stage.get("stage_name", "Skill Foundation")
                break
    missing_critical = list(latest_gap.missing_critical_skills or []) if latest_gap else []
    missing_secondary = list(latest_gap.missing_secondary_skills or []) if latest_gap else []
    all_missing = missing_critical + missing_secondary

    return {
        "profile": profile,
        "student_name": getattr(user, "full_name", None) or "Student",
        "degree": profile.degree or "B.Tech",
        "branch": profile.branch or "Computer Science",
        "cgpa": float(profile.cgpa or 7.5),
        "target_role": target_role,
        "target_company": target_company,
        "technical_skills": list(profile.technical_skills or []),
        "projects_count": len(profile.projects or []),
        "certifications_count": len(profile.certifications or []),
        "internships_count": len(profile.internships or []),
        "coding_score": float(profile.coding_score or 65.0),
        "aptitude_score": float(profile.aptitude_score or 65.0),
        "skill_match_percentage": float(latest_gap.match_percentage) if latest_gap else 60.0,
        "readiness_category": latest_readiness.predicted_status if latest_readiness else "Moderate Readiness",
        "placement_readiness_score": float(latest_readiness.readiness_score) if latest_readiness else 65.0,
        "top_missing_skills": all_missing[:4],
        "current_roadmap_stage": current_stage_name
    }


def _call_gemini_llm_if_available(prompt: str) -> Optional[str]:
    """Attempts to call Google Gemini API if GEMINI_API_KEY is configured in env."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        import urllib.request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 800}
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.info(f"Gemini API invocation skipped or failed: {e}. Using deterministic RAG synthesis.")
        return None


def answer_career_question(
    db: Session,
    user: User,
    question: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> CareerAssistantResponse:
    """
    RAG Pipeline:
    1. Gathers student career state.
    2. Retrieves top relevant knowledge chunks using FAISS.
    3. Synthesizes a grounded, personalized career answer with citations.
    """
    ctx = _get_student_context(db, user)

    # 1. Enhance retrieval query with student context
    augmented_query = f"{question} {ctx['target_role']} {' '.join(ctx['top_missing_skills'][:2])}"
    retrieved_raw = vector_store.search(augmented_query, top_k=3)

    retrieved_sources = [
        RetrievedKnowledgeChunk(
            chunk_id=r["chunk_id"],
            doc_id=r["doc_id"],
            title=r["title"],
            category=r["category"],
            tags=r.get("tags", []),
            content=r["content"],
            similarity_score=r["similarity_score"]
        )
        for r in retrieved_raw
    ]

    # Build student context schema
    student_ctx_obj = StudentCareerContext(
        student_name=ctx["student_name"],
        degree=ctx["degree"],
        branch=ctx["branch"],
        cgpa=ctx["cgpa"],
        target_role=ctx["target_role"],
        target_company=ctx["target_company"],
        skill_match_percentage=ctx["skill_match_percentage"],
        readiness_category=ctx["readiness_category"],
        placement_readiness_score=ctx["placement_readiness_score"],
        top_missing_skills=ctx["top_missing_skills"],
        current_roadmap_stage=ctx["current_roadmap_stage"]
    )

    # 2. Check for LLM generation
    sources_text = "\n\n".join([f"[{r.title} | {r.category}]: {r.content}" for r in retrieved_sources])
    system_prompt = f"""You are the AI Career Twin Assistant.
Student Profile:
- Name: {ctx['student_name']}, Degree: {ctx['degree']} in {ctx['branch']}, CGPA: {ctx['cgpa']}
- Target Role: {ctx['target_role']} at {ctx['target_company']}
- Skill Match: {ctx['skill_match_percentage']}% | Placement Readiness: {ctx['placement_readiness_score']}%
- Missing Skills: {', '.join(ctx['top_missing_skills'])}
- Current Roadmap Stage: {ctx['current_roadmap_stage']}

Retrieved Knowledge Base Sources:
{sources_text}

User Question: {question}

Instructions:
1. Provide a direct, highly personalized answer tailored to their exact target role and profile.
2. Ground technical recommendations strictly in the provided Knowledge Base sources.
3. Cite sources explicitly using [Source: Title].
4. If the required information is not available in the sources or profile, state clearly that it is unavailable.
5. Provide 2-3 concrete next action steps. Keep it professional, encouraging, and actionable."""

    llm_output = _call_gemini_llm_if_available(system_prompt)
    is_fallback = False

    if not llm_output:
        # High-quality deterministic RAG synthesis
        is_fallback = True
        llm_output = _synthesize_deterministic_answer(question, ctx, retrieved_sources)

    # 3. Dynamic follow-up questions
    followups = [
        f"What projects will best showcase my skills for {ctx['target_role']}?",
        f"How can I bridge my remaining gap in {ctx['top_missing_skills'][0] if ctx['top_missing_skills'] else 'System Architecture'}?",
        f"What should I focus on in the '{ctx['current_roadmap_stage']}' roadmap stage?"
    ]

    return CareerAssistantResponse(
        question=question,
        answer=llm_output,
        retrieved_sources=retrieved_sources,
        student_context=student_ctx_obj,
        suggested_followups=followups,
        is_fallback=is_fallback,
        generated_at=datetime.now(timezone.utc)
    )


def _synthesize_deterministic_answer(
    question: str,
    ctx: Dict[str, Any],
    sources: List[RetrievedKnowledgeChunk]
) -> str:
    """Grounded synthesis engine formatting structured answers with explicit citations."""
    q_lower = question.lower()
    target_role = ctx["target_role"]
    target_company = ctx["target_company"]
    missing_str = ", ".join(ctx["top_missing_skills"]) if ctx["top_missing_skills"] else "None identified"

    best_source = sources[0] if sources else None
    second_source = sources[1] if len(sources) > 1 else None

    # Scenario 1: Skills to learn or missing skills
    if any(k in q_lower for k in ["skill", "missing", "learn", "study"]):
        ans = f"""### Analysis for {target_role} at {target_company}

Based on your current skill profile and target requirements, your skill match is currently **{ctx['skill_match_percentage']}%**.

#### Priority Skill Gaps:
- **Missing Skills**: {missing_str}
- **Current Milestone**: You are in the **{ctx['current_roadmap_stage']}** phase.

#### Grounded Guidance:
"""
        if best_source:
            ans += f"- **{best_source.title}** ([Source: {best_source.title}]): {best_source.content[:240]}...\n"
        if second_source:
            ans += f"- **{second_source.title}** ([Source: {second_source.title}]): {second_source.content[:240]}...\n"

        ans += f"""
#### Recommended Action Steps:
1. Prioritize learning **{ctx['top_missing_skills'][0] if ctx['top_missing_skills'] else 'Core Architecture'}** this week.
2. Build a functional micro-module using this technology and integrate it into your GitHub repository.
3. Once completed, your skill match is projected to rise towards **{min(100.0, ctx['skill_match_percentage'] + 12.0):.1f}%**."""
        return ans

    # Scenario 2: Project recommendations
    if any(k in q_lower for k in ["project", "build", "portfolio", "capstone"]):
        ans = f"""### Project Strategy for {target_role}

To stand out for {target_company}, your projects must demonstrate real-world scalability and cover your critical skill gaps ({missing_str}).

#### Recommended Project Concept:
- **Title**: Distributed {target_role} Service Engine
- **Focus**: Incorporates your missing competencies ({missing_str}) alongside your existing strengths ({', '.join(ctx['technical_skills'][:3])}).
"""
        if best_source:
            ans += f"\n> **Knowledge Insight** ([Source: {best_source.title}]): {best_source.content}\n"

        ans += f"""
#### Implementation Blueprint:
1. **Repository Setup**: Initialize clean directory structure with Docker Compose, automated unit tests, and CI/CD workflow.
2. **Architecture**: Implement asynchronous REST API endpoints with robust error handling and database connection pooling.
3. **Deployment**: Deploy with live public demo URL and a clear README containing architecture diagrams."""
        return ans

    # Scenario 3: Placement readiness & preparation
    if any(k in q_lower for k in ["placement", "readiness", "score", "improve", "interview", "aptitude"]):
        ans = f"""### Placement Readiness Blueprint

Your current placement readiness is assessed at **{ctx['placement_readiness_score']}%** ({ctx['readiness_category']}).

#### Diagnostic Breakdown:
- **Coding Performance**: {ctx['coding_score']}/100
- **Aptitude Score**: {ctx['aptitude_score']}/100
- **Academics**: CGPA {ctx['cgpa']} ({ctx['degree']} {ctx['branch']})
"""
        if best_source:
            ans += f"\n#### Industry Preparation Standards ([Source: {best_source.title}]):\n{best_source.content}\n"

        ans += f"""
#### Immediate Improvements:
1. **Target Practice**: Daily problem solving focusing on high-frequency patterns (Two Pointers, Graphs, and Dynamic Programming).
2. **Interview Delivery**: Practice articulating technical decisions and behavioral STAR examples out loud.
3. **Roadmap Sync**: Complete your pending tasks in the **{ctx['current_roadmap_stage']}** stage."""
        return ans

    # Scenario 4: General fallback synthesis
    ans = f"""### Career Twin Guidance for {ctx['student_name']}

Here is tailored guidance for your career trajectory towards **{target_role}** at **{target_company}**:

"""
    if best_source:
        ans += f"#### From Knowledge Base: {best_source.title} ([Source: {best_source.title}])\n{best_source.content}\n\n"
    if second_source:
        ans += f"#### Related Insight: {second_source.title} ([Source: {second_source.title}])\n{second_source.content}\n\n"

    ans += f"""#### Status Summary:
- **Target Role**: {target_role} ({target_company})
- **Skill Match**: {ctx['skill_match_percentage']}% | **Placement Readiness**: {ctx['placement_readiness_score']}%
- **Next High-Priority Skill**: {ctx['top_missing_skills'][0] if ctx['top_missing_skills'] else 'Advanced System Architecture'}
- **Current Milestone**: {ctx['current_roadmap_stage']}"""
    return ans


def generate_llm_personalized_recommendations(
    db: Session,
    user: User
) -> LLMPersonalizedRecommendationResponse:
    """
    Synthesizes rich, personalized narrative recommendations explaining
    deterministic skill gaps and ML placement scores without altering calculated metrics.
    """
    ctx = _get_student_context(db, user)
    missing = ctx["top_missing_skills"]
    primary_missing = missing[0] if len(missing) > 0 else "Cloud Architecture & Docker"
    secondary_missing = missing[1] if len(missing) > 1 else "Relational SQL Indexing"

    next_skill = NextSkillRecommendation(
        skill=primary_missing,
        priority="High Priority",
        why_it_matters=f"Directly required by {ctx['target_company']} for the {ctx['target_role']} position. Resolving this gap boosts your skill-match from {ctx['skill_match_percentage']}% towards {min(100.0, ctx['skill_match_percentage'] + 12.0):.1f}%.",
        learning_path=f"Complete hands-on tutorials covering syntax, architecture, and production deployment patterns for {primary_missing} over the next 10 days."
    )

    project = ProjectRecommendation(
        title=f"Cloud-Native {ctx['target_role']} Capstone Platform",
        description=f"Build and deploy an enterprise-grade service integrating {primary_missing} and {secondary_missing} alongside your core competencies ({', '.join(ctx['technical_skills'][:2])}).",
        tech_stack=[primary_missing, secondary_missing] + ctx["technical_skills"][:2],
        target_impact="Provides proof of execution on your resume and directly validates readiness for technical hiring rounds."
    )

    priorities = [
        LearningPriorityItem(
            area=f"Core Competency: {primary_missing}",
            timeline="Weeks 1 - 2",
            rationale=f"Highest weight missing prerequisite for {ctx['target_role']} at {ctx['target_company']}."
        ),
        LearningPriorityItem(
            area="Coding Drills & Pattern Recognition",
            timeline="Weeks 2 - 4",
            rationale=f"Elevate coding score from {ctx['coding_score']} to 85+ to pass online screening assessments."
        ),
        LearningPriorityItem(
            area="Mock Technical & STAR Behavioral Interviews",
            timeline="Weeks 4 - 6",
            rationale="Simulate time-pressured technical explanations and refine your measurable impact stories."
        )
    ]

    interview_guide = InterviewPrepGuide(
        technical_drills=[
            f"Implement core data structures and service patterns using {primary_missing}",
            "Master Sliding Window, Graph DFS/BFS, and Dynamic Programming",
            "Explain ACID transactions, indexing strategies, and caching trade-offs"
        ],
        system_design_or_architecture=f"Study high-throughput distributed system components (Load Balancing, Redis caching, message queues) for {ctx['target_role']}.",
        behavioral_focus=f"Prepare 3 STAR stories highlighting technical problem-solving, collaboration, and learning from production defects aligned with {ctx['target_company']} values."
    )

    improvements = [
        f"Target learning {primary_missing} immediately to elevate your {ctx['skill_match_percentage']}% match score.",
        f"Add measurable metrics (latency reduction, user capacity) to existing projects in your profile and resume.",
        f"Consistently maintain practice tests to safeguard your {ctx['placement_readiness_score']}% placement readiness rating."
    ]

    return LLMPersonalizedRecommendationResponse(
        student_profile_id=ctx["profile"].id,
        target_role=ctx["target_role"],
        target_company=ctx["target_company"],
        deterministic_skill_match=ctx["skill_match_percentage"],
        deterministic_placement_score=ctx["placement_readiness_score"],
        next_skill_to_learn=next_skill,
        recommended_project=project,
        learning_priorities=priorities,
        interview_preparation=interview_guide,
        improvement_suggestions=improvements,
        generated_at=datetime.now(timezone.utc)
    )
