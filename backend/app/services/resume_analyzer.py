"""
Resume Analyzer Service
Performs NLP-based information extraction from cleaned resume text.
Uses regex + rule-based NLP taxonomy matching — no external datasets or external API dependencies.
"""
import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("app.services.resume_analyzer")

# ============================================================================
# MASTER SKILL TAXONOMY
# ============================================================================

PROGRAMMING_LANGUAGES = [
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
    "rust", "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "dart",
    "haskell", "perl", "lua", "julia", "assembly", "objective-c", "vba", "groovy",
    "cobol", "fortran", "shell", "bash", "powershell", "sql"
]

TECHNICAL_SKILLS = {
    "Web & Frontend": [
        "react", "react.js", "reactjs", "angular", "vue", "vue.js", "vuejs",
        "next.js", "nextjs", "svelte", "html", "html5", "css", "css3",
        "tailwind", "tailwindcss", "bootstrap", "redux", "graphql", "webpack",
        "vite", "jquery", "sass", "less", "material ui", "chakra ui"
    ],
    "Backend & APIs": [
        "fastapi", "django", "flask", "express", "express.js", "expressjs",
        "node.js", "nodejs", "spring", "springboot", "spring boot", "laravel",
        "rails", "ruby on rails", "asp.net", "rest api", "restful", "grpc",
        "microservices", "websockets"
    ],
    "Databases": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis",
        "cassandra", "elasticsearch", "oracle", "mssql", "sql server",
        "dynamodb", "firebase", "supabase", "neo4j", "mariadb"
    ],
    "AI, ML & Data": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "sklearn", "pandas", "numpy", "matplotlib", "seaborn",
        "nlp", "natural language processing", "computer vision", "opencv",
        "transformers", "hugging face", "bert", "gpt", "llm", "rag",
        "xgboost", "lightgbm", "random forest", "neural networks", "data analysis",
        "data visualization"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "gcp", "google cloud",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins",
        "github actions", "ci/cd", "linux", "nginx", "apache", "helm",
        "serverless", "lambda", "ec2", "s3", "cloudwatch"
    ],
    "Tools & Platforms": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "postman", "swagger", "figma", "vscode", "intellij", "jupyter",
        "colab", "tableau", "power bi", "excel", "spark", "hadoop", "kafka"
    ]
}

SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "critical thinking",
    "time management", "project management", "agile", "scrum", "collaboration",
    "adaptability", "analytical thinking", "creativity", "attention to detail",
    "public speaking", "mentoring", "research", "decision making"
]

# Section header patterns
SECTION_PATTERNS = {
    "education": [r"\beducation\b", r"\bacademic(?:s)?\b", r"\bqualifications?\b", r"\bdegree\b"],
    "experience": [r"\bexperience\b", r"\bwork experience\b", r"\bemployment\b", r"\bjob history\b", r"\bprofessional experience\b"],
    "projects": [r"\bprojects?\b", r"\bproject work\b", r"\bpersonal projects?\b", r"\bacademic projects?\b", r"\bkey projects\b"],
    "skills": [r"\bskills?\b", r"\btechnical skills?\b", r"\bcore competencies\b", r"\btechnical expertise\b", r"\btechnologies\b"],
    "certifications": [r"\bcertifications?\b", r"\bcertificates?\b", r"\bcredentials?\b", r"\baccreditations?\b", r"\blicenses?\b"],
    "internships": [r"\binternships?\b", r"\btrainee(?:ship)?\b", r"\bindustrial training\b"],
    "achievements": [r"\bachievements?\b", r"\bawards?\b", r"\bhonors?\b", r"\bhonours?\b"],
    "summary": [r"\bsummary\b", r"\bobjective\b", r"\bprofile\b", r"\babout me\b", r"\bcareer objective\b"],
}

DEGREE_PATTERNS = [
    r"\bb\.?tech(?:\.|\b)", r"\bb\.?e(?:\.|\b)", r"\bm\.?tech(?:\.|\b)", r"\bm\.?e(?:\.|\b)",
    r"\bb\.?sc(?:\.|\b)", r"\bm\.?sc(?:\.|\b)", r"\bmca\b", r"\bbca\b",
    r"\bph\.?d\b", r"\bbachelor\b", r"\bmaster(?:'s)?\b", r"\bdiploma\b", r"\bassociate\b"
]

BRANCH_KEYWORDS = [
    "computer science and engineering", "computer science", "information technology",
    "artificial intelligence and data science", "artificial intelligence", "data science",
    "software engineering", "electronics and communication", "electrical and electronics",
    "mechanical engineering", "civil engineering", "chemical engineering",
    "cse", "it", "ece", "eee", "mech", "civil"
]


def _match_term(term: str, text: str) -> bool:
    """
    Matches a term in text using boundary-safe regex.
    Special symbols like +, #, . are safely escaped.
    """
    escaped = re.escape(term)
    # Match if bounded by non-alphanumeric or start/end
    pattern = rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])"
    return bool(re.search(pattern, text, re.IGNORECASE))


def split_into_sections(text: str) -> Dict[str, str]:
    """
    Splits resume text into named sections based on header detection.
    """
    lines = text.split("\n")
    sections: Dict[str, List[str]] = {"header": []}
    current_section = "header"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_section = None
        # Headers are usually short lines (< 60 chars)
        if len(stripped) < 60:
            for section_name, patterns in SECTION_PATTERNS.items():
                for pat in patterns:
                    if re.search(pat, stripped, re.IGNORECASE):
                        matched_section = section_name
                        break
                if matched_section:
                    break

        if matched_section:
            current_section = matched_section
            if current_section not in sections:
                sections[current_section] = []
        else:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append(stripped)

    return {k: "\n".join(v) for k, v in sections.items()}


def extract_email(text: str) -> Optional[str]:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0).lower() if match else None


def extract_phone(text: str) -> Optional[str]:
    match = re.search(r"(\+?\d[\d\s\-().]{8,15}\d)", text)
    return match.group(0).strip() if match else None


def extract_name(text: str) -> Optional[str]:
    """Heuristic: extract full candidate name from first 5 lines."""
    first_lines = text.strip().split("\n")[:5]
    for line in first_lines:
        stripped = line.strip()
        # Candidate name: 2-4 words, alphabetic, no digits, < 50 chars
        words = stripped.split()
        if 2 <= len(words) <= 4 and not re.search(r"\d", stripped) and len(stripped) < 50:
            if not any(header in stripped.lower() for header in ["resume", "curriculum", "cv", "profile", "contact"]):
                return stripped.title()
    return None


def extract_links(text: str) -> Dict[str, Optional[str]]:
    links: Dict[str, Optional[str]] = {
        "linkedin_url": None,
        "github_url": None,
        "portfolio_url": None
    }
    # LinkedIn
    m_li = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    if m_li:
        links["linkedin_url"] = f"https://linkedin.com/in/{m_li.group(1)}"
    
    # GitHub
    m_gh = re.search(r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    if m_gh:
        links["github_url"] = f"https://github.com/{m_gh.group(1)}"
        
    # Portfolio / personal website
    m_web = re.search(r"https?://(?!linkedin|github)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,5}(?:/[^\s]*)?", text, re.IGNORECASE)
    if m_web:
        links["portfolio_url"] = m_web.group(0)
        
    return links


def extract_education(text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
    edu_text = sections.get("education", "") or text
    found: List[Dict[str, Any]] = []

    for pattern in DEGREE_PATTERNS:
        for m in re.finditer(pattern, edu_text, re.IGNORECASE):
            start = max(0, m.start() - 30)
            end = min(len(edu_text), m.end() + 150)
            context = edu_text[start:end].strip()

            # Find year
            year_m = re.search(r"\b(20\d{2}|19\d{2})\b", context)
            year = int(year_m.group(1)) if year_m else None

            # Find branch
            branch = None
            for bk in BRANCH_KEYWORDS:
                if bk in context.lower():
                    branch = bk.upper()
                    break

            degree_name = m.group(0).upper().replace(".", "")

            entry = {
                "degree": degree_name,
                "branch": branch or "Not specified",
                "year": year,
                "context": context[:120]
            }

            # Deduplicate by degree and year
            if not any(e["degree"] == entry["degree"] and e["year"] == entry["year"] for e in found):
                found.append(entry)

    return found[:5]


def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extracts technical skills and programming languages from text.
    Uses regex boundary matching to prevent partial matches.
    """
    found_langs: List[str] = []
    found_tech: List[str] = []

    # Programming languages
    for lang in PROGRAMMING_LANGUAGES:
        if _match_term(lang, text):
            # Format display name
            display = lang.upper() if lang in ["sql", "php", "r", "c", "vba"] else lang.title()
            display = display.replace(".Js", ".js").replace("++", "++").replace("#", "#")
            found_langs.append(display)

    # Technical skills
    for category, skills_list in TECHNICAL_SKILLS.items():
        for skill in skills_list:
            if _match_term(skill, text):
                display = skill.upper() if skill in ["html", "html5", "css", "css3", "aws", "gcp", "k8s", "nlp", "rag", "llm", "gpt", "bert"] else skill.title()
                display = display.replace(".Js", ".js")
                if display not in found_tech:
                    found_tech.append(display)

    # Deduplicate preserving order
    return {
        "programming_languages": list(dict.fromkeys(found_langs)),
        "technical_skills": list(dict.fromkeys(found_tech))
    }


def extract_soft_skills_from_text(text: str) -> List[str]:
    found = []
    for skill in SOFT_SKILLS:
        if _match_term(skill, text):
            found.append(skill.title())
    return list(dict.fromkeys(found))


def extract_projects(text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
    proj_text = sections.get("projects", "")
    if not proj_text:
        return []

    projects: List[Dict[str, Any]] = []
    lines = [l.strip() for l in proj_text.split("\n") if l.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        # Lines that look like project titles
        if 3 < len(line) < 100 and (line[0].isupper() or line.startswith(("-", "•", "*", "·", "#"))):
            title = line.lstrip("-•*·# ").strip()
            desc_lines = []
            j = i + 1
            while j < len(lines) and not (len(lines[j]) < 80 and lines[j][0:1].isupper() and j > i + 1):
                desc_lines.append(lines[j])
                j += 1

            combined = title + " " + " ".join(desc_lines)
            skills_info = extract_skills_from_text(combined)
            tech_stack = (skills_info["programming_languages"] + skills_info["technical_skills"])[:6]

            projects.append({
                "title": title[:100],
                "description": " ".join(desc_lines)[:300] if desc_lines else "",
                "tech_stack": tech_stack
            })
            i = j
        else:
            i += 1

    return projects[:8]


def extract_certifications(text: str, sections: Dict[str, str]) -> List[Dict[str, Any]]:
    cert_text = sections.get("certifications", "") or text
    certs: List[Dict[str, Any]] = []

    cert_patterns = [
        r"(aws certified[\w\s\-]+)",
        r"(google cloud certified[\w\s\-]+)",
        r"(microsoft certified[\w\s\-]+)",
        r"(oracle certified[\w\s\-]+)",
        r"(cisco ccna[\w\s\-]*)",
        r"(cisco ccnp[\w\s\-]*)",
        r"(certified[\w\s\-]+practitioner)",
        r"(certified[\w\s\-]+developer)",
        r"(coursera[\s:–\-]+[\w\s]+(?:specialization|course)?)",
        r"(udemy[\s:–\-]+[\w\s]+)",
        r"([\w\s]+certificate[\w\s]*)",
        r"([\w\s]+certification[\w\s]*)"
    ]

    seen = set()
    for pattern in cert_patterns:
        for m in re.finditer(pattern, cert_text, re.IGNORECASE):
            cert_name = m.group(1).strip()[:100]
            clean_name = re.sub(r"[\n\r]+", " ", cert_name).strip()
            key = clean_name.lower()[:35]
            if len(clean_name) > 6 and not any(skip in clean_name.lower() for skip in ["education", "experience", "projects"]):
                # Avoid subphrase duplicates
                if not any(clean_name.lower() in c["title"].lower() or c["title"].lower() in clean_name.lower() for c in certs):
                    seen.add(key)
                    issuer = "Not specified"
                    for iss in ["AWS", "Amazon", "Google", "Microsoft", "Oracle", "Cisco", "Coursera", "Udemy", "Meta", "IBM"]:
                        if iss.lower() in clean_name.lower():
                            issuer = iss
                            break
                    certs.append({"title": clean_name, "issuer": issuer})

    return certs[:8]


def extract_internships_and_experience(text: str, sections: Dict[str, str]) -> Dict[str, Any]:
    """
    Extracts both internships and professional experience entries.
    Returns dict: {"internships": [...], "experience": [...], "experience_years": float}
    """
    exp_text = sections.get("experience", "") or ""
    intern_text = sections.get("internships", "") or ""
    combined_exp = (intern_text + "\n" + exp_text) if (intern_text or exp_text) else text

    internships: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []

    patterns = [
        r"([A-Za-z\s]{3,40}?)\s+(?:at|@|–|-)\s+([A-Za-z0-9\s&,\.]{2,40}?)\s*(?:\(([^)]+)\)|((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})[^\n]{0,35}))",
        r"(intern(?:ship)?)\s*(?:at|@|in|–|-)\s*([A-Za-z0-9\s&,\.]{2,40})",
        r"([A-Za-z\s]{3,35}\s+developer|engineer|analyst|intern|trainee)\s+(?:at|@|for)\s+([A-Za-z0-9\s&,\.]{2,40})"
    ]

    seen = set()
    for pattern in patterns:
        for m in re.finditer(pattern, combined_exp, re.IGNORECASE):
            role = m.group(1).strip()[:60]
            company = m.group(2).strip()[:60] if m.lastindex and m.lastindex >= 2 else "Unknown"
            duration = (m.group(3) or m.group(4) or "").strip() if m.lastindex and m.lastindex >= 3 and m.group(3) else "Not specified"

            # Clean up company name
            company = re.sub(r"[\n\r]+", " ", company).strip()
            role = re.sub(r"[\n\r]+", " ", role).strip()

            key = (role.lower()[:20], company.lower()[:20])
            # Check if this company is already added
            existing_companies = [c["company"].lower() for c in (internships + experience)]
            if len(company) > 2 and len(role) > 2 and company.lower() not in existing_companies:
                seen.add(key)
                entry = {
                    "role": role.title(),
                    "company": company.title(),
                    "duration": duration,
                    "duration_months": 3
                }
                if "intern" in role.lower() or "intern" in company.lower() or "trainee" in role.lower():
                    internships.append(entry)
                else:
                    experience.append(entry)

    total_exp_count = len(internships) + len(experience)
    exp_years = round(total_exp_count * 0.5, 1)

    return {
        "internships": internships[:6],
        "experience": experience[:6],
        "experience_years": exp_years
    }


def calculate_ats_score(
    text: str,
    technical_skills: List[str],
    programming_languages: List[str],
    education: List[Dict],
    projects: List[Dict],
    certifications: List[Dict],
    internships: List[Dict],
    experience: List[Dict],
    name: Optional[str],
    email: Optional[str],
    phone: Optional[str],
    links: Dict[str, Optional[str]],
) -> Dict[str, Any]:
    """
    Calculates weighted ATS completeness score (0-100) with category breakdown.
    """
    breakdown = {
        "Contact Info": {"score": 0, "max": 15, "feedback": []},
        "Skills & Languages": {"score": 0, "max": 25, "feedback": []},
        "Education": {"score": 0, "max": 15, "feedback": []},
        "Projects": {"score": 0, "max": 20, "feedback": []},
        "Experience & Internships": {"score": 0, "max": 15, "feedback": []},
        "Format & Readability": {"score": 0, "max": 10, "feedback": []},
    }

    # 1. Contact Info (15 pts)
    if name:
        breakdown["Contact Info"]["score"] += 4
    else:
        breakdown["Contact Info"]["feedback"].append("Full name missing at the top of resume.")

    if email:
        breakdown["Contact Info"]["score"] += 5
    else:
        breakdown["Contact Info"]["feedback"].append("Professional email address not found.")

    if phone:
        breakdown["Contact Info"]["score"] += 3
    else:
        breakdown["Contact Info"]["feedback"].append("Contact phone number missing.")

    if links.get("linkedin_url"):
        breakdown["Contact Info"]["score"] += 2
    else:
        breakdown["Contact Info"]["feedback"].append("LinkedIn profile link recommended for ATS.")

    if links.get("github_url"):
        breakdown["Contact Info"]["score"] += 1

    # 2. Skills & Languages (25 pts)
    total_skills = len(technical_skills) + len(programming_languages)
    if total_skills >= 10:
        breakdown["Skills & Languages"]["score"] = 25
    elif total_skills >= 7:
        breakdown["Skills & Languages"]["score"] = 20
    elif total_skills >= 4:
        breakdown["Skills & Languages"]["score"] = 15
    elif total_skills >= 2:
        breakdown["Skills & Languages"]["score"] = 8
    else:
        breakdown["Skills & Languages"]["score"] = 3
        breakdown["Skills & Languages"]["feedback"].append("Add more explicit technical skills and frameworks.")

    if len(programming_languages) == 0:
        breakdown["Skills & Languages"]["feedback"].append("Specify core programming languages clearly (e.g. Python, Java, C++).")

    # 3. Education (15 pts)
    if education:
        breakdown["Education"]["score"] += 10
        if any(e.get("year") for e in education):
            breakdown["Education"]["score"] += 5
        else:
            breakdown["Education"]["feedback"].append("Add graduation year for education entries.")
    else:
        breakdown["Education"]["feedback"].append("Degree or education qualifications missing.")

    # 4. Projects (20 pts)
    proj_count = len(projects)
    if proj_count >= 3:
        breakdown["Projects"]["score"] = 20
    elif proj_count == 2:
        breakdown["Projects"]["score"] = 15
    elif proj_count == 1:
        breakdown["Projects"]["score"] = 9
    else:
        breakdown["Projects"]["feedback"].append("Include 2-3 detailed technical projects with tech stack descriptions.")

    # 5. Experience & Internships (15 pts)
    total_exp_items = len(internships) + len(experience)
    if total_exp_items >= 2:
        breakdown["Experience & Internships"]["score"] = 15
    elif total_exp_items == 1:
        breakdown["Experience & Internships"]["score"] = 10
    else:
        breakdown["Experience & Internships"]["score"] = 4
        breakdown["Experience & Internships"]["feedback"].append("Include internship experience or practical industry training.")

    # 6. Format & Readability (10 pts)
    words = len(text.split())
    if 250 <= words <= 850:
        breakdown["Format & Readability"]["score"] = 10
    elif words < 250:
        breakdown["Format & Readability"]["score"] = 5
        breakdown["Format & Readability"]["feedback"].append(f"Resume text is very brief ({words} words). Add more details.")
    else:
        breakdown["Format & Readability"]["score"] = 7
        breakdown["Format & Readability"]["feedback"].append(f"Resume is quite long ({words} words). Aim for a concise single/dual page format.")

    total_score = sum(item["score"] for item in breakdown.values())
    max_score = sum(item["max"] for item in breakdown.values())
    percentage = round((total_score / max_score) * 100, 1)

    if percentage >= 85:
        rating = "Excellent"
    elif percentage >= 70:
        rating = "Good"
    elif percentage >= 50:
        rating = "Fair"
    else:
        rating = "Needs Improvement"

    return {
        "total_score": percentage,
        "rating": rating,
        "breakdown": breakdown,
        "word_count": words
    }


def compare_with_profile(
    resume_technical_skills: List[str],
    resume_prog_languages: List[str],
    profile_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Compares extracted resume skills and details with the student's existing profile.
    Identifies:
    1. Skills in resume but missing from profile
    2. Skills in profile but missing from resume
    3. Important profile information missing from resume
    """
    profile_data = profile_data or {}
    prof_tech = profile_data.get("technical_skills") or []
    prof_langs = profile_data.get("programming_languages") or []

    resume_all_lower = {s.lower() for s in (resume_technical_skills + resume_prog_languages)}
    profile_all_lower = {s.lower() for s in (prof_tech + prof_langs)}

    # 1. Skills in resume but missing from profile
    skills_to_add_to_profile = [
        s for s in (resume_technical_skills + resume_prog_languages)
        if s.lower() not in profile_all_lower
    ]

    # 2. Skills in profile but missing from resume
    skills_missing_from_resume = [
        s for s in (prof_tech + prof_langs)
        if s.lower() not in resume_all_lower
    ]

    # 3. Important profile information missing from resume
    missing_profile_info = []

    # Check social/portfolio links
    if profile_data.get("github_url") and not profile_data.get("resume_has_github"):
        missing_profile_info.append(f"GitHub profile ({profile_data['github_url']}) is set in your profile but missing from your resume.")

    if profile_data.get("linkedin_url") and not profile_data.get("resume_has_linkedin"):
        missing_profile_info.append(f"LinkedIn URL is configured in your profile but not found in your resume.")

    if profile_data.get("portfolio_url") and not profile_data.get("resume_has_portfolio"):
        missing_profile_info.append(f"Portfolio website ({profile_data['portfolio_url']}) is not mentioned in your resume.")

    if profile_data.get("phone") and not profile_data.get("resume_has_phone"):
        missing_profile_info.append("Phone number listed in your profile is missing from your resume.")

    # Check academic data
    if profile_data.get("college_name") and not profile_data.get("resume_has_college"):
        missing_profile_info.append(f"College/University name ({profile_data['college_name']}) is not explicitly recognized in your resume.")

    if profile_data.get("cgpa") and float(profile_data.get("cgpa", 0)) >= 7.0 and not profile_data.get("resume_has_cgpa"):
        missing_profile_info.append(f"Strong CGPA ({profile_data['cgpa']}) from your profile is missing from your resume.")

    # Check profile projects
    profile_projects = profile_data.get("projects") or []
    if profile_projects and len(profile_data.get("resume_projects") or []) < len(profile_projects):
        missing_count = len(profile_projects) - len(profile_data.get("resume_projects") or [])
        missing_profile_info.append(f"{missing_count} project(s) recorded in your career profile are not detected in your resume.")

    # Check profile certifications
    profile_certs = profile_data.get("certifications") or []
    if profile_certs and len(profile_data.get("resume_certs") or []) == 0:
        missing_profile_info.append(f"You have {len(profile_certs)} certification(s) in your profile that are missing from your resume.")

    # Check profile internships
    profile_interns = profile_data.get("internships") or []
    if profile_interns and len(profile_data.get("resume_internships") or []) == 0:
        missing_profile_info.append("Internship experience saved in your profile was not detected in your resume.")

    return {
        "skills_to_add_to_profile": list(dict.fromkeys(skills_to_add_to_profile)),
        "skills_missing_from_resume": list(dict.fromkeys(skills_missing_from_resume)),
        "missing_profile_info": missing_profile_info
    }


def analyze_resume(
    cleaned_text: str,
    profile_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Master analysis function.
    Orchestrates extraction, ATS calculation, and student profile comparison.
    """
    profile_data = profile_data or {}

    # Step 1: Split into sections
    sections = split_into_sections(cleaned_text)

    # Step 2: Contact info
    name = extract_name(cleaned_text)
    email = extract_email(cleaned_text)
    phone = extract_phone(cleaned_text)
    links = extract_links(cleaned_text)

    # Step 3: Education
    education = extract_education(cleaned_text, sections)

    # Step 4: Skills extraction
    skills_context = sections.get("skills", "") + "\n" + cleaned_text
    skills_info = extract_skills_from_text(skills_context)
    soft_skills = extract_soft_skills_from_text(cleaned_text)

    technical_skills = skills_info["technical_skills"]
    programming_languages = skills_info["programming_languages"]

    # Step 5: Projects
    projects = extract_projects(cleaned_text, sections)

    # Step 6: Certifications
    certifications = extract_certifications(cleaned_text, sections)

    # Step 7: Internships and Experience
    exp_info = extract_internships_and_experience(cleaned_text, sections)
    internships = exp_info["internships"]
    experience = exp_info["experience"]
    exp_years = exp_info["experience_years"]

    # Step 8: ATS Score Calculation
    ats_result = calculate_ats_score(
        text=cleaned_text,
        technical_skills=technical_skills,
        programming_languages=programming_languages,
        education=education,
        projects=projects,
        certifications=certifications,
        internships=internships,
        experience=experience,
        name=name,
        email=email,
        phone=phone,
        links=links,
    )

    # Prepare flags for profile comparison
    enhanced_profile_data = dict(profile_data)
    enhanced_profile_data["resume_has_github"] = bool(links.get("github_url"))
    enhanced_profile_data["resume_has_linkedin"] = bool(links.get("linkedin_url"))
    enhanced_profile_data["resume_has_portfolio"] = bool(links.get("portfolio_url"))
    enhanced_profile_data["resume_has_phone"] = bool(phone)
    enhanced_profile_data["resume_has_college"] = (
        profile_data.get("college_name", "").lower() in cleaned_text.lower()
    ) if profile_data.get("college_name") else True
    enhanced_profile_data["resume_has_cgpa"] = bool(re.search(r"\b(?:cgpa|gpa|percentage)[\s:]*([0-9\.]+)", cleaned_text, re.IGNORECASE))
    enhanced_profile_data["resume_projects"] = projects
    enhanced_profile_data["resume_certs"] = certifications
    enhanced_profile_data["resume_internships"] = internships

    # Step 9: Profile Comparison
    comparison = compare_with_profile(
        resume_technical_skills=technical_skills,
        resume_prog_languages=programming_languages,
        profile_data=enhanced_profile_data,
    )

    # Step 10: Suggestions and Strengths
    improvements_suggested = []
    if not name:
        improvements_suggested.append("Place your full name prominently at the top header.")
    if not email:
        improvements_suggested.append("Add a professional email address.")
    if not phone:
        improvements_suggested.append("Include your contact phone number.")
    if not links.get("linkedin_url"):
        improvements_suggested.append("Add your LinkedIn profile link.")
    if not links.get("github_url"):
        improvements_suggested.append("Include your GitHub profile for code sample verification.")
    if len(projects) < 2:
        improvements_suggested.append("Add at least 2-3 technical projects with tools and achievements.")
    if len(internships) + len(experience) == 0:
        improvements_suggested.append("Add relevant internship, part-time, or open-source contribution experience.")
    if len(technical_skills) + len(programming_languages) < 6:
        improvements_suggested.append("Expand your technical skills list to match target industry keywords.")
    if not education:
        improvements_suggested.append("Include your degree, institution, and expected graduation year in an Education section.")
    if len(certifications) == 0:
        improvements_suggested.append("Add recognized certifications (AWS, Google, Coursera, etc.) to enhance credibility.")

    # Strengths
    strengths = []
    if len(technical_skills) >= 6:
        strengths.append(f"Strong technical skill set detected with {len(technical_skills)} industry skills.")
    if len(programming_languages) >= 2:
        strengths.append(f"Demonstrates versatility across {len(programming_languages)} programming languages.")
    if len(projects) >= 2:
        strengths.append(f"Solid portfolio with {len(projects)} hands-on projects identified.")
    if len(certifications) >= 1:
        strengths.append(f"Recognized certifications detected ({len(certifications)} found).")
    if len(internships) + len(experience) >= 1:
        strengths.append("Practical internship or industrial experience listed.")
    if links.get("github_url"):
        strengths.append("GitHub profile provided for technical evaluation.")
    if links.get("linkedin_url"):
        strengths.append("Professional LinkedIn profile link present.")
    if ats_result["total_score"] >= 75:
        strengths.append(f"High ATS completeness rating ({ats_result['total_score']}%) with well-defined sections.")

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin_url": links.get("linkedin_url"),
        "github_url": links.get("github_url"),
        "portfolio_url": links.get("portfolio_url"),
        "education": education,
        "technical_skills": technical_skills,
        "programming_languages": programming_languages,
        "soft_skills": soft_skills,
        "projects": projects,
        "certifications": certifications,
        "internships": internships,
        "experience": experience,
        "extracted_experience_years": exp_years,
        "ats_score": ats_result["total_score"],
        "ats_rating": ats_result["rating"],
        "ats_breakdown": ats_result["breakdown"],
        "word_count": ats_result["word_count"],
        "strengths": strengths,
        "improvements_suggested": improvements_suggested,
        "skills_to_add_to_profile": comparison["skills_to_add_to_profile"],
        "skills_missing_from_resume": comparison["skills_missing_from_resume"],
        "missing_profile_info": comparison["missing_profile_info"],
        "profile_comparison": comparison,
        "sections_detected": list(sections.keys()),
    }
