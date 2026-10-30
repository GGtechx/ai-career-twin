"""
Company and Job Service
Manages company profiles, job roles, requirements, and sample development seeding.
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.models import Company, JobRole, JobRequirement
from app.models.student_profile import StudentProfile
from app.models.user import User

logger = logging.getLogger("app.services.company_job_service")

# ============================================================================
# SAMPLE / DEVELOPMENT SEED DATA (10 Companies, 15 Job Roles)
# Clearly marked as SAMPLE/DEVELOPMENT data.
# ============================================================================

SAMPLE_COMPANIES = [
    {
        "name": "Google",
        "industry": "Internet / Cloud / AI",
        "tier": "Tier 1",
        "website": "https://careers.google.com",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] Global technology leader in search, cloud systems, generative AI, and distributed software engineering."
    },
    {
        "name": "Microsoft",
        "industry": "Enterprise Cloud / Software",
        "tier": "Tier 1",
        "website": "https://careers.microsoft.com",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] Pioneer in operating systems, enterprise cloud (Azure), productivity software, and AI systems."
    },
    {
        "name": "Amazon",
        "industry": "E-Commerce / Cloud Computing",
        "tier": "Tier 1",
        "website": "https://amazon.jobs",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] World's largest cloud provider (AWS) and e-commerce platform focusing on high-scale distributed systems."
    },
    {
        "name": "Razorpay",
        "industry": "FinTech / Payment Systems",
        "tier": "Tier 1",
        "website": "https://razorpay.com/jobs",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] Leading Indian FinTech unicorn powering online payment gateways, banking, and credit workflows."
    },
    {
        "name": "Swiggy",
        "industry": "Consumer Tech / Logistics",
        "tier": "Tier 1",
        "website": "https://swiggy.com/careers",
        "logo_url": "https://upload.wikimedia.org/wikipedia/en/1/12/Swiggy_logo.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] On-demand hyper-local convenience and food delivery platform driven by data science and routing algorithms."
    },
    {
        "name": "Cisco Systems",
        "industry": "Networking / Cyber Security",
        "tier": "Tier 1",
        "website": "https://jobs.cisco.com",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/0/08/Cisco_logo_blue_2016.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] Worldwide leader in IT and networking hardware, software, telecommunications, and high-security protocols."
    },
    {
        "name": "Tata Consultancy Services (TCS)",
        "industry": "IT Services & Consulting",
        "tier": "Tier 2",
        "website": "https://tcs.com/careers",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Tata_Consultancy_Services_Logo.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] Largest multinational IT service and consulting firm in India delivering global enterprise transformation."
    },
    {
        "name": "Infosys",
        "industry": "Digital Transformation / Services",
        "tier": "Tier 2",
        "website": "https://infosys.com/careers",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/9/95/Infosys_logo.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] Global leader in next-generation digital services and consulting enabling clients across 56 countries."
    },
    {
        "name": "Accenture",
        "industry": "Management Consulting / Tech",
        "tier": "Tier 2",
        "website": "https://accenture.com/careers",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Accenture.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] Fortune Global 500 company providing strategy, consulting, digital, technology, and operations services."
    },
    {
        "name": "Tata Elxsi",
        "industry": "Embedded Systems / AI Design",
        "tier": "Tier 2",
        "website": "https://tataelxsi.com/careers",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Tata_Elxsi_Logo.svg",
        "hiring_status": "Active",
        "description": "[SAMPLE/DEVELOPMENT DATA] Specialized design and technology services company focusing on automotive, broadcast, IoT, and healthcare AI."
    }
]

SAMPLE_JOB_ROLES = [
    {
        "company_name": "Google",
        "title": "Software Development Engineer (SDE I)",
        "domain": "Distributed Systems / Backend",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 18.0,
        "package_max_lpa": 28.0,
        "location": "Bengaluru / Hyderabad",
        "description": "[SAMPLE DATA] Design and implement highly available distributed cloud services and foundational algorithmic backends at planetary scale.",
        "requirements": {
            "min_cgpa": 8.0,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "ECE"],
            "must_have_skills": ["Python", "C++", "Java", "Data Structures", "Algorithms"],
            "good_to_have_skills": ["Distributed Systems", "Docker", "Kubernetes", "Linux", "gRPC"],
            "min_internships_count": 1,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Google",
        "title": "Machine Learning Engineer",
        "domain": "Artificial Intelligence / ML",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 22.0,
        "package_max_lpa": 32.0,
        "location": "Bengaluru",
        "description": "[SAMPLE DATA] Train and deploy large language models, computer vision systems, and neural ranking systems for Google applications.",
        "requirements": {
            "min_cgpa": 8.2,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "AI/DS"],
            "must_have_skills": ["Python", "PyTorch", "TensorFlow", "Machine Learning", "Deep Learning"],
            "good_to_have_skills": ["Transformers", "NLP", "Computer Vision", "Scikit-Learn", "Docker"],
            "min_internships_count": 1,
            "min_projects_count": 3
        }
    },
    {
        "company_name": "Microsoft",
        "title": "Cloud Software Engineer",
        "domain": "Cloud Infrastructure",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 16.0,
        "package_max_lpa": 25.0,
        "location": "Bengaluru / Noida",
        "description": "[SAMPLE DATA] Build resilient multi-tenant microservices and edge architectures for Microsoft Azure cloud platform.",
        "requirements": {
            "min_cgpa": 7.5,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "ECE", "EEE"],
            "must_have_skills": ["C#", "Python", "Docker", "Microservices", "REST API"],
            "good_to_have_skills": ["Azure", "Kubernetes", "Go", "PostgreSQL", "CI/CD"],
            "min_internships_count": 1,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Microsoft",
        "title": "Frontend Software Engineer",
        "domain": "Web & UI Systems",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 14.0,
        "package_max_lpa": 22.0,
        "location": "Hyderabad",
        "description": "[SAMPLE DATA] Craft accessible, ultra-responsive web interfaces for Microsoft 365 and web applications using modern web stacks.",
        "requirements": {
            "min_cgpa": 7.2,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT"],
            "must_have_skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS"],
            "good_to_have_skills": ["Next.js", "Redux", "Tailwind", "Jest", "GraphQL"],
            "min_internships_count": 0,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Amazon",
        "title": "Software Development Engineer (Backend)",
        "domain": "Backend & Distributed Systems",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 18.0,
        "package_max_lpa": 26.0,
        "location": "Bengaluru / Chennai",
        "description": "[SAMPLE DATA] Architect mission-critical high-throughput payment and checkout services handling millions of TPS on AWS.",
        "requirements": {
            "min_cgpa": 7.5,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "ECE"],
            "must_have_skills": ["Java", "Python", "Data Structures", "Algorithms", "REST API"],
            "good_to_have_skills": ["AWS", "DynamoDB", "PostgreSQL", "Redis", "Kafka"],
            "min_internships_count": 1,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Amazon",
        "title": "DevOps & Cloud Engineer",
        "domain": "Site Reliability / Cloud",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 15.0,
        "package_max_lpa": 23.0,
        "location": "Hyderabad",
        "description": "[SAMPLE DATA] Automate deployment pipelines, monitoring telemetry, infrastructure as code, and cluster orchestration on AWS.",
        "requirements": {
            "min_cgpa": 7.0,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "ECE", "EEE"],
            "must_have_skills": ["Linux", "Docker", "Python", "CI/CD", "AWS"],
            "good_to_have_skills": ["Kubernetes", "Terraform", "Ansible", "Bash", "Prometheus"],
            "min_internships_count": 0,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Razorpay",
        "title": "FinTech Backend Engineer",
        "domain": "Financial Systems / Payments",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 15.0,
        "package_max_lpa": 22.0,
        "location": "Bengaluru",
        "description": "[SAMPLE DATA] Build rock-solid financial transaction ledger pipelines, webhook dispatcher engines, and fraud prevention filters.",
        "requirements": {
            "min_cgpa": 7.5,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT"],
            "must_have_skills": ["Go", "Python", "PostgreSQL", "Redis", "REST API"],
            "good_to_have_skills": ["Kafka", "Microservices", "Docker", "SQL", "FastAPI"],
            "min_internships_count": 1,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Razorpay",
        "title": "Full Stack Developer",
        "domain": "Full Stack Web",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 13.0,
        "package_max_lpa": 20.0,
        "location": "Bengaluru",
        "description": "[SAMPLE DATA] Deliver end-to-end merchant portal experiences and developer dashboards across React and Node.js/Python backends.",
        "requirements": {
            "min_cgpa": 7.0,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT"],
            "must_have_skills": ["React", "JavaScript", "TypeScript", "Node.js", "PostgreSQL"],
            "good_to_have_skills": ["FastAPI", "Tailwind", "Docker", "Redis", "Git"],
            "min_internships_count": 0,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Swiggy",
        "title": "Data Scientist / Decision Analyst",
        "domain": "Analytics & Machine Learning",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 16.0,
        "package_max_lpa": 24.0,
        "location": "Bengaluru",
        "description": "[SAMPLE DATA] Develop dynamic dispatch optimization, delivery duration prediction models, and customer recommendation engines.",
        "requirements": {
            "min_cgpa": 7.5,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "AI/DS", "Math"],
            "must_have_skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "Machine Learning"],
            "good_to_have_skills": ["Tableau", "PyTorch", "Data Analysis", "A/B Testing", "Spark"],
            "min_internships_count": 1,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Swiggy",
        "title": "Mobile App Engineer (React Native / Android)",
        "domain": "Mobile Applications",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 12.0,
        "package_max_lpa": 18.0,
        "location": "Bengaluru",
        "description": "[SAMPLE DATA] Craft snappy high-performance consumer app interfaces with real-time GPS tracking and fluid cart animations.",
        "requirements": {
            "min_cgpa": 7.0,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT"],
            "must_have_skills": ["JavaScript", "React", "Mobile Development", "REST API", "Git"],
            "good_to_have_skills": ["TypeScript", "Kotlin", "Redux", "Android Studio", "Firebase"],
            "min_internships_count": 0,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Cisco Systems",
        "title": "Cyber Security & Network Engineer",
        "domain": "Network Security",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 12.0,
        "package_max_lpa": 18.0,
        "location": "Bengaluru",
        "description": "[SAMPLE DATA] Test intrusion detection platforms, firewall firmware, zero-trust network policy enforcers, and packet analysis tools.",
        "requirements": {
            "min_cgpa": 7.0,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "ECE"],
            "must_have_skills": ["Python", "C", "Linux", "Networking", "Cyber Security"],
            "good_to_have_skills": ["Wireshark", "CCNA", "Cryptography", "TCP/IP", "Docker"],
            "min_internships_count": 0,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Tata Consultancy Services (TCS)",
        "title": "Digital Innovator / Systems Engineer",
        "domain": "Enterprise IT",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 7.5,
        "package_max_lpa": 11.5,
        "location": "Mumbai / Pune / Bengaluru",
        "description": "[SAMPLE DATA] Accelerate client IT modernization through enterprise web applications, data migration, and automated testing.",
        "requirements": {
            "min_cgpa": 6.5,
            "max_active_backlogs": 1,
            "eligible_branches": ["CSE", "IT", "ECE", "EEE", "Mechanical", "Civil"],
            "must_have_skills": ["Java", "Python", "SQL", "Problem Solving"],
            "good_to_have_skills": ["HTML", "CSS", "Spring Boot", "Git", "Cloud Computing"],
            "min_internships_count": 0,
            "min_projects_count": 1
        }
    },
    {
        "company_name": "Infosys",
        "title": "Specialist Programmer (Power Programmer)",
        "domain": "Software Engineering",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 8.0,
        "package_max_lpa": 12.0,
        "location": "Bengaluru / Mysuru / Pune",
        "description": "[SAMPLE DATA] High-impact programming role building enterprise APIs, real-time analytics engines, and microservices.",
        "requirements": {
            "min_cgpa": 6.8,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "ECE"],
            "must_have_skills": ["Java", "Python", "Data Structures", "Algorithms", "SQL"],
            "good_to_have_skills": ["Spring Boot", "Docker", "React", "PostgreSQL", "Git"],
            "min_internships_count": 0,
            "min_projects_count": 2
        }
    },
    {
        "company_name": "Accenture",
        "title": "Advanced Technology Associate",
        "domain": "Cloud & System Integration",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 8.5,
        "package_max_lpa": 12.5,
        "location": "Bengaluru / Hyderabad / Gurugram",
        "description": "[SAMPLE DATA] Integrate multi-cloud workflows, configure enterprise middleware, and build modern API pipelines.",
        "requirements": {
            "min_cgpa": 6.5,
            "max_active_backlogs": 1,
            "eligible_branches": ["CSE", "IT", "ECE", "EEE"],
            "must_have_skills": ["Python", "SQL", "Problem Solving", "Communication"],
            "good_to_have_skills": ["AWS", "Azure", "JavaScript", "Agile", "Linux"],
            "min_internships_count": 0,
            "min_projects_count": 1
        }
    },
    {
        "company_name": "Tata Elxsi",
        "title": "Embedded AI & Edge Systems Engineer",
        "domain": "Autonomous Systems / Embedded",
        "role_type": "Full-Time",
        "experience_level": "Entry-Level",
        "package_min_lpa": 9.0,
        "package_max_lpa": 14.0,
        "location": "Bengaluru / Thiruvananthapuram",
        "description": "[SAMPLE DATA] Optimize edge deep learning models for automotive ADAS systems, smart cameras, and embedded microcontrollers.",
        "requirements": {
            "min_cgpa": 7.0,
            "max_active_backlogs": 0,
            "eligible_branches": ["CSE", "IT", "ECE", "EEE"],
            "must_have_skills": ["C++", "Python", "Linux", "Data Structures"],
            "good_to_have_skills": ["OpenCV", "TensorFlow", "Computer Vision", "Embedded C", "Git"],
            "min_internships_count": 0,
            "min_projects_count": 2
        }
    }
]


def seed_sample_companies_and_jobs(db: Session) -> Dict[str, int]:
    """
    Seeds 10 sample companies and 15 sample job roles with full requirement records
    if the database is currently empty.
    """
    existing_companies_count = db.query(Company).count()
    if existing_companies_count >= 10:
        logger.info(f"Sample companies already exist ({existing_companies_count} found). Skipping seeding.")
        return {"companies": existing_companies_count, "jobs": db.query(JobRole).count()}

    logger.info("Seeding 10 sample companies and 15 job roles...")
    
    company_map: Dict[str, Company] = {}
    for comp_data in SAMPLE_COMPANIES:
        existing = db.query(Company).filter(Company.name == comp_data["name"]).first()
        if not existing:
            comp = Company(**comp_data)
            db.add(comp)
            db.flush()
            company_map[comp_data["name"]] = comp
        else:
            company_map[comp_data["name"]] = existing

    # Seed Job Roles and Requirements
    jobs_created = 0
    for job_data in SAMPLE_JOB_ROLES:
        company = company_map.get(job_data["company_name"])
        if not company:
            continue

        existing_job = db.query(JobRole).filter(
            JobRole.company_id == company.id,
            JobRole.title == job_data["title"]
        ).first()

        if not existing_job:
            req_data = job_data["requirements"]
            job = JobRole(
                company_id=company.id,
                title=job_data["title"],
                domain=job_data["domain"],
                role_type=job_data["role_type"],
                experience_level=job_data["experience_level"],
                package_min_lpa=job_data["package_min_lpa"],
                package_max_lpa=job_data["package_max_lpa"],
                location=job_data["location"],
                description=job_data["description"],
                is_active=True
            )
            db.add(job)
            db.flush()

            job_req = JobRequirement(
                job_role_id=job.id,
                min_cgpa=req_data["min_cgpa"],
                max_active_backlogs=req_data["max_active_backlogs"],
                eligible_branches=req_data["eligible_branches"],
                must_have_skills=req_data["must_have_skills"],
                good_to_have_skills=req_data["good_to_have_skills"],
                min_internships_count=req_data["min_internships_count"],
                min_projects_count=req_data["min_projects_count"]
            )
            db.add(job_req)
            jobs_created += 1

    db.commit()
    logger.info(f"Sample data successfully seeded! Companies: {len(company_map)}, Jobs created: {jobs_created}")
    return {"companies": len(company_map), "jobs": db.query(JobRole).count()}


def list_companies(db: Session, search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns list of companies with their active job counts."""
    query = db.query(Company)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(Company.name.ilike(s), Company.industry.ilike(s), Company.description.ilike(s)))
    
    companies = query.order_by(Company.tier.asc(), Company.name.asc()).all()
    results = []
    for c in companies:
        active_jobs = db.query(JobRole).filter(JobRole.company_id == c.id, JobRole.is_active == True).count()
        results.append({
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "tier": c.tier,
            "website": c.website,
            "logo_url": c.logo_url,
            "hiring_status": c.hiring_status,
            "description": c.description,
            "created_at": c.created_at,
            "active_jobs_count": active_jobs
        })
    return results


def get_company_detail(db: Session, company_id: int) -> Optional[Company]:
    return db.query(Company).filter(Company.id == company_id).first()


def list_job_roles(db: Session, company_id: Optional[int] = None, domain: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns all active job roles with company metadata."""
    query = db.query(JobRole).filter(JobRole.is_active == True)
    if company_id:
        query = query.filter(JobRole.company_id == company_id)
    if domain:
        query = query.filter(JobRole.domain.ilike(f"%{domain.strip()}%"))

    jobs = query.order_by(JobRole.package_max_lpa.desc().nullslast()).all()
    results = []
    for j in jobs:
        results.append({
            "id": j.id,
            "company_id": j.company_id,
            "company_name": j.company.name if j.company else "Unknown",
            "company_tier": j.company.tier if j.company else None,
            "company_logo_url": j.company.logo_url if j.company else None,
            "title": j.title,
            "domain": j.domain,
            "role_type": j.role_type,
            "experience_level": j.experience_level,
            "package_min_lpa": j.package_min_lpa,
            "package_max_lpa": j.package_max_lpa,
            "location": j.location,
            "description": j.description,
            "is_active": j.is_active,
            "created_at": j.created_at
        })
    return results


def get_job_role_with_requirements(db: Session, job_role_id: int) -> Optional[Dict[str, Any]]:
    """Returns full job role details and associated requirements."""
    job = db.query(JobRole).filter(JobRole.id == job_role_id).first()
    if not job:
        return None

    req = job.job_requirement
    req_dict = None
    if req:
        req_dict = {
            "id": req.id,
            "job_role_id": req.job_role_id,
            "min_cgpa": req.min_cgpa,
            "max_active_backlogs": req.max_active_backlogs,
            "eligible_branches": req.eligible_branches or [],
            "must_have_skills": req.must_have_skills or [],
            "good_to_have_skills": req.good_to_have_skills or [],
            "min_internships_count": req.min_internships_count,
            "min_projects_count": req.min_projects_count
        }

    return {
        "id": job.id,
        "company_id": job.company_id,
        "company_name": job.company.name if job.company else "Unknown",
        "company_tier": job.company.tier if job.company else None,
        "company_logo_url": job.company.logo_url if job.company else None,
        "title": job.title,
        "domain": job.domain,
        "role_type": job.role_type,
        "experience_level": job.experience_level,
        "package_min_lpa": job.package_min_lpa,
        "package_max_lpa": job.package_max_lpa,
        "location": job.location,
        "description": job.description,
        "is_active": job.is_active,
        "created_at": job.created_at,
        "requirement": req_dict
    }


def format_career_target_dict(job: JobRole, company_name: str, profile_id: Optional[int] = None, message: Optional[str] = None) -> Dict[str, Any]:
    req = job.job_requirement if job else None
    must_have = list(req.must_have_skills or []) if req and req.must_have_skills else []
    good_to_have = list(req.good_to_have_skills or []) if req and req.good_to_have_skills else []
    req_dict = {
        "min_cgpa": req.min_cgpa if req else 7.0,
        "max_active_backlogs": req.max_active_backlogs if req else 0,
        "eligible_branches": req.eligible_branches if req else ["CSE", "IT", "ECE"],
        "must_have_skills": must_have,
        "good_to_have_skills": good_to_have,
        "min_internships_count": req.min_internships_count if req else 0,
        "min_projects_count": req.min_projects_count if req else 2
    } if req else {}
    return {
        "id": job.id if job else None,
        "company_id": job.company_id if job else None,
        "company_name": company_name,
        "company_tier": job.company.tier if (job and job.company) else "Tier 1",
        "job_id": job.id if job else None,
        "job_title": job.title if job else None,
        "title": job.title if job else None,
        "domain": job.domain if job else "Software Engineering",
        "role_type": job.role_type if job else "Full-Time",
        "experience_level": job.experience_level if job else "Entry-Level",
        "package_min_lpa": job.package_min_lpa if job else 10.0,
        "package_max_lpa": job.package_max_lpa if job else 20.0,
        "location": job.location if job else "Bengaluru / Hybrid",
        "description": job.description if job else None,
        "required_skills": must_have,
        "requirements": req_dict,
        "requirement": req_dict,
        "experience_requirements": job.experience_level if job else "Entry-Level",
        "preferred_skills": good_to_have,
        "student_profile_id": profile_id or (job.id if job else 1),
        "target_job_role_id": job.id if job else 1,
        "target_job_title": job.title if job else "",
        "target_company_name": company_name,
        "message": message or f"Target job set to '{job.title if job else ''}' at {company_name}."
    }


def get_student_career_target(db: Session, user: User) -> Optional[Dict[str, Any]]:
    """Retrieves full standardized global career target for the student."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile or not profile.target_job_role:
        return None

    seed_sample_companies_and_jobs(db)
    job = None
    if profile.target_company:
        job = db.query(JobRole).join(Company).filter(
            JobRole.title == profile.target_job_role,
            Company.name == profile.target_company
        ).first()
    if not job:
        job = db.query(JobRole).filter(JobRole.title == profile.target_job_role).first()
    if not job:
        return None

    company_name = job.company.name if job.company else (profile.target_company or "Tech Company")
    return format_career_target_dict(job, company_name, profile.id)


def set_student_target_job(db: Session, user: User, job_role_id: int) -> Dict[str, Any]:
    """
    Updates the student profile's target_company and target_job_role,
    and immediately cascades target synchronization to all dependent modules:
    Skill Gap, Recommendations, Roadmap, and Digital Twin.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Student profile not found. Please complete profile first.")

    job = db.query(JobRole).filter(JobRole.id == job_role_id).first()
    if not job:
        raise ValueError("Job role not found.")

    company_name = job.company.name if job.company else "Tech Company"
    profile.target_company = company_name
    profile.target_job_role = job.title
    db.commit()
    db.refresh(profile)

    # 1. Immediately evaluate / refresh skill gap for this target job
    try:
        from app.services.skill_gap_service import analyze_skill_gap
        analyze_skill_gap(db, user, job.id)
    except Exception as e:
        logger.warning(f"Auto-update skill gap on target change: {e}")

    # 2. Immediately refresh recommendations for this target job
    try:
        from app.services.recommendation_service import generate_personalized_recommendations
        generate_personalized_recommendations(db, user, force_refresh=True)
    except Exception as e:
        logger.warning(f"Auto-update recommendations on target change: {e}")

    # 3. Immediately refresh roadmap for this target job
    try:
        from app.services.roadmap_service import generate_career_roadmap
        generate_career_roadmap(db, user, force_refresh=True)
    except Exception as e:
        logger.warning(f"Auto-update roadmap on target change: {e}")

    # 4. Synchronize Digital Career Twin
    try:
        from app.services.career_twin_service import on_profile_or_activity_updated
        on_profile_or_activity_updated(db, user, f"Target Job Selected: {job.title} at {company_name}")
    except Exception as e:
        logger.warning(f"Auto-sync twin on target change: {e}")

    return format_career_target_dict(
        job,
        company_name,
        profile.id,
        message=f"Successfully set target to '{job.title}' at {company_name}!"
    )

