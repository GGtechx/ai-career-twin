# AI Digital Career Twin Platform: Autonomous Career Intelligence, Skill Gap Diagnostics & What-If Simulation

---

## 1. Project Title
**AI Digital Career Twin: An Intelligent Cyber-Physical Student Avatar for Automated Career Path Optimization, Predictive Placement Analytics, and RAG Guidance**

---

## 2. Project Abstract
In higher education engineering ecosystems, students frequently struggle to align their evolving academic profiles, coding proficiencies, and resume portfolios with rapidly shifting corporate hiring requirements. The **AI Digital Career Twin Platform** bridges this gap by creating an intelligent, autonomous digital avatar representing each student's multi-dimensional competencies. Integrating machine learning classification trained on a 100,000-record benchmark placement dataset, natural language processing (NLP) skill normalization with TF-IDF cosine similarity matching, Retrieval-Augmented Generation (RAG) powered by a FAISS dense vector store, and a deterministic 7-stage career roadmap engine, the system delivers real-time placement readiness probability, customized skill-gap roadmaps, and an interactive "What-If" career sandbox for prospective capability modeling.

---

## 3. Problem Statement
Engineering students face critical structural hurdles when preparing for campus recruitment:
1. **Opaque Industry Benchmarks**: Lack of visibility into role-specific prerequisites and company-tier expectations.
2. **Static Career Advice**: Generic, non-personalized advice detached from empirical student performance telemetry.
3. **Ineffective Resume Portfolios**: Inability to diagnose resume ATS compatibility, missing critical technical competencies, and project deficits before applying.
4. **Absence of Sandbox Experimentation**: No predictive mechanism to simulate how acquiring a specific credential, framework, or coding score improvement translates into placement likelihood and compensation outcomes.

---

## 4. Objectives
- Construct an authenticated multi-tiered platform with persistent student telemetry across 21 relational database tables.
- Parse and analyze PDF resumes to extract technical competencies, projects, and calculate deterministic ATS completeness scores.
- Model company eligibility criteria and job role requirements across 10 sample enterprises and 15 job roles.
- Implement an NLP skill-gap engine calculating weighted cosine similarity and prioritizing critical versus secondary deficits.
- Train and deploy a high-efficiency Random Forest classifier predicting placement status and salary packages using live student attributes without runtime CSV overhead.
- Engineer a 7-stage personalized career roadmap with progress logging and task milestone checkoffs.
- Develop a local FAISS-indexed RAG career assistant providing grounded answers with source citations.
- Architect an interactive Digital Career Twin with a non-destructive "What-If" simulation sandbox.

---

## 5. Proposed System
The proposed architecture operates as a closed-loop intelligence feedback system:
1. **Ingestion & Parsing**: Student credentials, coursework, coding metrics, and uploaded PDF resumes are ingested and parsed.
2. **Diagnostic Evaluation**: The profile is benchmarked against target job roles, triggering NLP skill normalization, TF-IDF cosine gap scoring, and machine learning placement readiness inference.
3. **Synthesis & Roadmapping**: An algorithmic recommendation engine maps gaps to courses, certifications, and drills, constructing a dynamic 7-stage roadmap.
4. **Digital Twin Representation**: A multi-dimensional competency vector (Coding, Aptitude, Projects, Communication, Logical, Leadership) is mapped into a persistent Digital Career Twin with cohort percentile benchmarks.
5. **Interactive Exploration & RAG Assistance**: Students interact with an internal FAISS vector knowledge assistant and test potential career interventions using the What-If simulation engine.

---

## 6. System Architecture

```
[ Student / Browser (React + Vite) ]
                │
                ▼ (HTTP / REST APIs - Bearer JWT)
[ FastAPI Backend Application (Port 8000) ]
   ├── Authentication & Role Guard (JWT / Bcrypt)
   ├── Profile & Resume Analysis Engine (pdfplumber / Regex NLP)
   ├── Company & Job Requirements Engine (10 Companies, 15 Roles)
   ├── Skill Gap Analyzer (NLP Synonym Normalization + TF-IDF Cosine Matcher)
   ├── Placement Readiness Inference Service (Preloaded Scikit-Learn Model)
   ├── Personalized Recommendations Engine (Weighted Priority Scorer)
   ├── Career Roadmap Service (7-Stage Timeline & Task Progress Tracker)
   ├── RAG Assistant Engine (FAISS Dense Vector Store + Grounded Synthesizer)
   └── Digital Career Twin Engine (State Sync + What-If Simulation Sandbox)
                │
     ┌──────────┴──────────┐
     ▼                     ▼
[ PostgreSQL / SQLite ] [ AI Artifacts & FAISS Index ]
- 21 Database Tables   - placement_classifier.joblib
- User / Profiles      - model_metadata.json
- Resumes / Gaps       - faiss_index.bin
- Roadmaps / Twin      - embedding_pipeline.joblib
- Progress Tracking    - career_documents.json
```

---

## 7. Modules

### Module 1: Authentication & Student Profile Management
- Secure user registration and login with bcrypt password hashing and JWT access tokens.
- Complete student telemetry: academics, CGPA, backlogs, technical/soft skills, programming languages, projects, certifications, internships, and target career goals.

### Module 2: PDF Resume ATS Analysis
- In-memory PDF text extraction using `pdfplumber` and `pypdf`.
- Clean text extraction pipeline identifying education, programming languages, technical skills, projects, certifications, and experience.
- ATS completeness scoring and profile-vs-resume cross-comparison.

### Module 3: Company & Job Requirements Module
- Curated database of 10 enterprise companies (Google, Microsoft, Amazon, Atlassian, TCS, etc.) and 15 job roles.
- Eligibility requirements: minimum CGPA, eligible branches, maximum backlogs, internship/project prerequisites, and weighted must-have vs good-to-have skill specifications.
- Target role selection API persisting user intent.

### Module 4: Skill Gap Analysis Module
- Multi-phase skill normalization using a domain synonym taxonomy map.
- TF-IDF character n-gram cosine matching comparing student skills against job prerequisites.
- Categorization into matched skills, critical missing skills, secondary missing skills, priority rankings, and readiness tiers.

### Module 5: Placement Readiness Prediction Module
- Machine learning classification trained on 100,000 student records from the base-paper placement dataset.
- Evaluates student CGPA, internships, projects, certifications, coding scores, aptitude, communication, mock interviews, and backlogs.
- Completely decoupled live inference from model artifact (`ai-model/models/placement_classifier.joblib`) without re-reading the CSV file at runtime.
- Predicts placement status, readiness score (0-100), placement probability, strengths, risk areas, and estimated salary packages (LPA).

### Module 6: Personalized Recommendations & Career Roadmap
- 7-category recommendation engine (Skills, Courses, Projects, Certifications, Coding drills, Aptitude practice, and Interview preparation).
- Dynamic 7-stage career roadmap: *Skill Foundation*, *Skill Development*, *Project Development*, *Certification*, *Coding & Aptitude*, *Interview Preparation*, and *Placement Ready*.
- Interactive task completion checkoffs and progress persistence in the `progress_tracking` table.

### Module 7: Career Knowledge Base & RAG Assistant
- Internal career knowledge base structured across 13 domains.
- Local chunking and 128-dimensional dense semantic embedding pipeline.
- FAISS `IndexFlatIP` vector index providing sub-millisecond semantic retrieval.
- Grounded RAG assistant at `POST /ai/career-assistant` providing personalized answers with explicit citations (`[Source: {title}]`).

### Module 8: Digital Career Twin & Update Engine
- Unified digital avatar persisted in the `digital_career_twin` table.
- Multi-dimensional competency vectors (Coding, Aptitude, Projects, Communication, Logical, Leadership) and cohort percentile benchmarking.
- Automatic update engine recalculating skill gaps, placement odds, and twin state upon profile or roadmap changes.

### Module 9: What-If Career Simulation Sandbox
- Non-destructive simulation at `POST /twin/simulate`.
- Allows students to simulate hypothetical skill acquisitions, capstone project completions, coding score gains, or internships.
- Computes projected deltas in skill match %, placement readiness score, and salary package without modifying permanent database records.

### Module 10: Main Student Dashboard
- Unified executive overview aggregating live student telemetry across profile, resume ATS score, skill match %, target job, placement probability, roadmap progress, Career Twin radar, and priority action items.

---

## 8. Methodology
1. **Offline Training Phase**:
   - The 100,000-row base-paper CSV is preprocessed and used to train a Random Forest classifier.
   - The fitted model, feature rankings, and evaluation metrics are serialized to disk (`ai-model/models/`).
2. **Offline Vector Indexing Phase**:
   - Structured career documents across 13 domains are tokenized, transformed into 128-dimensional L2-normalized dense embeddings, and indexed into FAISS (`faiss_index.bin`).
3. **Online Operational Phase**:
   - Authenticated student requests interact strictly with the live database (PostgreSQL / SQLite).
   - Predictions and RAG queries load lightweight pre-compiled artifacts in memory, achieving sub-100ms response times with zero external dataset re-parsing.

---

## 9. Algorithms & Techniques
- **Classification**: Random Forest Classifier with Gini impurity split criterion, 100 estimators, and maximum depth of 12.
- **Natural Language Processing (NLP)**:
  - Technical synonym mapping & lemmatization.
  - Sub-word and character n-gram TF-IDF vectorization.
  - Cosine similarity matching ($S_C(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$).
- **Dense Vector Search**:
  - Truncated Singular Value Decomposition (SVD) dimensionality reduction.
  - FAISS (Facebook AI Similarity Search) Inner Product index (`IndexFlatIP`).
- **Telemetry Scoring**:
  - Weighted multi-attribute ranking for digital twin competency vectors.
  - Sigmoidal cohort percentile mapping.

---

## 10. Dataset Description: Base-Paper vs. Application Database

> **IMPORTANT DISTINCTION**:
> - **Base-Paper Dataset (`datasets/base-paper/student_placement_prediction_dataset_2026.csv`)**:
>   - A benchmark dataset consisting of **100,000 student academic and placement records** across 26 features (CGPA, internships, projects, certifications, aptitude scores, coding performance, soft skills, and placement status).
>   - **Purpose**: Exclusively utilized for offline ML model training, feature importance extraction, and baseline hyperparameter tuning.
>   - **Runtime Constraint**: The application does **NOT** reload or query this large CSV file during live API execution.
> - **Live Application Database (PostgreSQL / SQLite)**:
>   - Stores live student accounts, profiles, uploaded resumes, company requirements, skill gap records, placement predictions, recommendations, roadmaps, and Digital Career Twin states.
>   - All interactive user operations read from and write to this database.

---

## 11. Technology Stack
- **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn
- **Machine Learning & NLP**: Scikit-Learn, NumPy, Pandas, Joblib, SciPy, FAISS (`faiss-cpu`)
- **PDF Extraction**: `pdfplumber`, `pypdf`, `pdfminer.six`
- **Security & Auth**: PyJWT, Bcrypt, Passlib
- **Database**: PostgreSQL (Production) / SQLite `career_twin.db` (Local Dev)
- **Frontend**: React 18, Vite, React Router v6, Vanilla CSS (Design Tokens, Glassmorphism, Micro-animations)
- **Testing**: Pytest, FastAPI TestClient, AnyIO

---

## 12. Database Architecture
The relational database comprises 21 fully normalized tables:
1. `users`: Credentials, roles, authentication state.
2. `student_profiles`: Academic and career profile records.
3. `academic_records`: Semester-wise SGPA and marks.
4. `skills`: Master skill taxonomy catalog.
5. `student_skills`: Student-specific skill associations and proficiency levels.
6. `projects`: Portfolio project repositories and tech stacks.
7. `certifications`: Industry credentials and issuers.
8. `internships`: Professional experience and durations.
9. `coding_performance`: LeetCode/HackerRank metrics and scores.
10. `aptitude_performance`: Quantitative and verbal metrics.
11. `resumes`: Parsed resume text, metadata, and ATS scores.
12. `companies`: Enterprise hiring partners.
13. `job_roles`: Corporate job roles and packages.
14. `job_requirements`: Minimum criteria and required skill weights.
15. `skill_gap_results`: Normalized matching results and gap priorities.
16. `placement_readiness`: ML placement predictions and factor scores.
17. `courses`: Learning catalog and mapped competencies.
18. `career_roadmaps`: 7-stage roadmap milestones.
19. `recommendations`: Multi-category action items and statuses.
20. `digital_career_twin`: Digital avatar state, radar scores, and percentiles.
21. `progress_tracking`: Audit log of milestone and task completions.

---

## 13. API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register student user |
| `POST` | `/auth/login` | Authenticate student & receive JWT |
| `GET` | `/profile/me` | Retrieve authenticated student profile |
| `PUT` | `/profile/me` | Update student profile & trigger Twin sync |
| `POST` | `/resume/upload` | Upload & parse PDF resume with ATS scoring |
| `GET` | `/resume/my-resume` | Retrieve latest uploaded resume analysis |
| `GET` | `/companies` | List all hiring companies (with search filter) |
| `GET` | `/jobs` | List active job roles (with company filter) |
| `GET` | `/jobs/my-target` | Retrieve student's target job requirements |
| `POST` | `/jobs/{id}/select-target` | Set target job role & update career twin |
| `POST` | `/skill-gap/analyze/{id}` | Execute NLP skill gap analysis |
| `GET` | `/skill-gap/latest` | Retrieve latest skill gap record |
| `POST` | `/placement/predict` | Run live ML placement inference |
| `GET` | `/placement/latest` | Retrieve latest placement assessment |
| `GET` | `/recommendations` | Get categorized career recommendations |
| `PATCH`| `/recommendations/{id}/complete` | Mark recommendation as completed |
| `GET` | `/roadmap` | Retrieve 7-stage personalized roadmap |
| `PATCH`| `/roadmap/tasks/{id}` | Update roadmap task completion & log progress |
| `POST` | `/ai/career-assistant` | Grounded RAG Career Assistant question-answering |
| `GET` | `/ai/recommendations` | Narrative LLM recommendations explaining scores |
| `GET` | `/twin/state` | Retrieve Digital Career Twin state & radar |
| `POST` | `/twin/sync` | Explicitly trigger Career Twin recalculation |
| `POST` | `/twin/simulate` | Non-destructive What-If career simulation |
| `GET` | `/dashboard/summary` | Unified student dashboard telemetry aggregation |

---

## 14. AI & RAG Architecture
- **Knowledge Base**: 16 comprehensive, structured document modules in `backend/app/knowledge_base/career_documents.json`.
- **Chunking Pipeline**: Semantic sliding window chunker with overlapping boundaries.
- **Dense Vector Embeddings**: Fitted sub-word TF-IDF + TruncatedSVD pipeline generating 128-dimensional L2-normalized dense continuous vectors.
- **Vector Index**: FAISS `IndexFlatIP` persisted to `faiss_index.bin`.
- **Grounded Synthesizer**: Ingests student telemetry + top-3 retrieved knowledge chunks; formats responses with explicit source citations.
- **Offline Reliability**: Gracefully falls back to high-grade deterministic synthesis if external LLM API keys are absent or unavailable.

---

## 15. Digital Career Twin Architecture
The Digital Career Twin operates as an active state machine:
- **State Vector**:
  $$\mathbf{V}_{\text{twin}} = [S_{\text{coding}}, S_{\text{aptitude}}, S_{\text{projects}}, S_{\text{comm}}, S_{\text{logical}}, S_{\text{leadership}}]$$
- **Composite Score**:
  $$S_{\text{overall}} = 0.25 S_{\text{coding}} + 0.20 S_{\text{aptitude}} + 0.20 S_{\text{projects}} + 0.15 S_{\text{comm}} + 0.10 S_{\text{logical}} + 0.10 S_{\text{leadership}}$$
- **Update Engine**: Event-driven hooks on profile mutations, roadmap completions, or target job changes trigger automatic state updates.
- **What-If Simulation**: Computes simulated deltas ($\Delta \text{Match}\%$, $\Delta \text{Readiness}\%$, $\Delta \text{LPA}$) without persisting changes to the core profile.

---

## 16. Installation Instructions

### Prerequisites
- Python 3.11+ (Python 3.13 tested)
- Node.js 18+ and npm
- (Optional) PostgreSQL 14+ (Local SQLite is used automatically if PostgreSQL is unavailable)

### Clone & Environment Setup
```bash
git clone <repository_url>
cd career_project
```

---

## 17. Environment Variables
Create `backend/.env` (or copy from `backend/.env.example`):
```env
PROJECT_NAME="AI Digital Career Twin"
API_V1_PREFIX="/api/v1"
SECRET_KEY="your-secure-jwt-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/career_twin"
GEMINI_API_KEY="" # Optional: For external Gemini LLM refinement
```

---

## 18. How to Run Backend
```bash
cd backend
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/health`

---

## 19. How to Run Frontend
```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 20. How to Run Tests
From the project root:
```bash
# Run complete test suite (all 7 suites, 62 automated tests)
.\backend\venv\Scripts\python.exe -m pytest tests/ -v
```

---

## 21. Project Limitations
- Resume text extraction relies on standard PDF text streams; scanned raster images without OCR layers require external tesseract preprocessing.
- The base-paper classification model reflects historical campus recruitment patterns; specialized off-campus recruitment dynamics may require separate fine-tuning.
- Local dense embeddings are optimized for technical career taxonomy and may require domain re-fitting for non-engineering disciplines.

---

## 22. Future Enhancements
- Integration of Optical Character Recognition (OCR) for scanned graphical resumes.
- Multi-agent interview simulation sidecar conducting live audio/video mock technical assessments.
- Real-time scrapers syncing campus placement cell drive notifications directly into the corporate job role catalog.
- Micro-credential verification via cryptographic verifiable credentials or blockchain records.
