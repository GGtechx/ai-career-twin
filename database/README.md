# Database Layer: AI Digital Career Twin

This folder contains database initializers, schema documentation, and SQL DDL scripts for the PostgreSQL live application database.

---

## 21 Relational Tables Overview

| Table Name | Description | Key Relationships |
| :--- | :--- | :--- |
| `users` | User credentials, emails, roles (student/admin), and active status | 1-to-1 with `student_profiles` |
| `student_profiles` | Demographics, roll no, college, tier, branch, graduation year, social links | Parent of student attributes |
| `academic_records` | CGPA, 10th/12th marks, active & history backlogs, attendance % | 1-to-1 with `student_profiles` |
| `skills` | Master catalog of technical and soft skills | 1-to-M with `student_skills` |
| `student_skills` | Association of student to skills with proficiency (0-100) & verification | M:N bridge with metadata |
| `projects` | Student portfolio projects, tech stacks, complexity, GitHub/live links | M-to-1 with `student_profiles` |
| `certifications` | Professional certificates, issuers, verification IDs, skills covered | M-to-1 with `student_profiles` |
| `internships` | Industry work experience, roles, duration, descriptions | M-to-1 with `student_profiles` |
| `coding_performance` | LeetCode counts, Codeforces rating, GitHub repos, coding score | 1-to-1 with `student_profiles` |
| `aptitude_performance` | Quantitative, logical, verbal, mock interview & aptitude scores | 1-to-1 with `student_profiles` |
| `resumes` | Uploaded resumes, file paths, parsed text, ATS scores, feedback | M-to-1 with `student_profiles` |
| `companies` | Target employers, tiers (FAANG/Unicorn/Service), industry | 1-to-M with `job_roles` |
| `job_roles` | Specific positions (SDE-1, Data Scientist, Cloud Engineer) | Belongs to `companies` |
| `job_requirements` | CGPA cutoffs, backlogs limit, must-have skills, project minima | 1-to-1 with `job_roles` |
| `skill_gap_results` | Match %, matching vs missing critical/secondary skills | Student to Job Role bridge |
| `placement_readiness` | ML-predicted placement probability, projected salary range, factors | Evaluated for student profile |
| `courses` | Curated online learning courses mapped to skills | Recommended to students |
| `career_roadmaps` | Weekly milestone roadmap to bridge skill gaps for a target role | Student to Job Role bridge |
| `recommendations` | System & AI generated advice for courses, skills, and projects | M-to-1 with `student_profiles` |
| `digital_career_twin` | Virtual persona: 6-axis radar scores, percentile, what-if state | 1-to-1 with `student_profiles` |
| `progress_tracking` | Action item completion logs, roadmap task tracking, milestones | M-to-1 with `student_profiles` |

---

## Initializing the Database

### Option A: Automatic via FastAPI Startup
Whenever the backend server starts (`python -m app.main`), SQLAlchemy automatically creates all missing tables.

### Option B: Standalone Script
```bash
python database/init_db.py
```

### Option C: Direct PostgreSQL DDL Script
```bash
psql -U postgres -d career_twin -f database/schema.sql
```

---

## PostgreSQL Setup Guide
1. Ensure PostgreSQL is installed and running on port `5432`.
2. Create the target database:
   ```sql
   CREATE DATABASE career_twin;
   ```
3. Update `backend/.env`:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/career_twin
   ```
4. If PostgreSQL is offline, the backend automatically utilizes SQLite fallback (`career_twin.db`) so development is never blocked.
