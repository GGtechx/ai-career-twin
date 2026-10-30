-- ============================================================================
-- AI DIGITAL CAREER TWIN - POSTGRESQL DATABASE SCHEMA (21 TABLES)
-- Generated for PostgreSQL 14+ / 15+ / 16+
-- ============================================================================

-- Table: companies
CREATE TABLE companies (
	id SERIAL NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	industry VARCHAR(100), 
	tier VARCHAR(30), 
	website VARCHAR(255), 
	logo_url VARCHAR(255), 
	hiring_status VARCHAR(50), 
	description TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

-- Table: courses
CREATE TABLE courses (
	id SERIAL NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	provider VARCHAR(100) NOT NULL, 
	url VARCHAR(500) NOT NULL, 
	domain VARCHAR(100), 
	difficulty_level VARCHAR(30), 
	duration_hours FLOAT, 
	rating FLOAT, 
	is_free BOOLEAN, 
	mapped_skills JSON, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

-- Table: skills
CREATE TABLE skills (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	category VARCHAR(50) NOT NULL, 
	description TEXT, 
	popularity_score FLOAT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

-- Table: users
CREATE TABLE users (
	id SERIAL NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	full_name VARCHAR(150) NOT NULL, 
	role VARCHAR(50) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

-- Table: job_roles
CREATE TABLE job_roles (
	id SERIAL NOT NULL, 
	company_id INTEGER, 
	title VARCHAR(150) NOT NULL, 
	domain VARCHAR(100) NOT NULL, 
	role_type VARCHAR(50), 
	experience_level VARCHAR(50), 
	package_min_lpa FLOAT, 
	package_max_lpa FLOAT, 
	location VARCHAR(100), 
	description TEXT, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(company_id) REFERENCES companies (id) ON DELETE SET NULL
);

-- Table: student_profiles
CREATE TABLE student_profiles (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	roll_number VARCHAR(50), 
	phone VARCHAR(20), 
	date_of_birth DATE, 
	gender VARCHAR(20), 
	college_name VARCHAR(255), 
	college_tier VARCHAR(20), 
	branch VARCHAR(100), 
	graduation_year INTEGER, 
	current_year INTEGER, 
	current_semester INTEGER, 
	bio TEXT, 
	linkedin_url VARCHAR(255), 
	github_url VARCHAR(255), 
	leetcode_url VARCHAR(255), 
	portfolio_url VARCHAR(255), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Table: academic_records
CREATE TABLE academic_records (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	tenth_percentage FLOAT, 
	twelfth_percentage FLOAT, 
	cgpa FLOAT NOT NULL, 
	backlogs_active INTEGER NOT NULL, 
	backlogs_history INTEGER NOT NULL, 
	attendance_percentage FLOAT NOT NULL, 
	semester_gpas JSON, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (student_profile_id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: aptitude_performance
CREATE TABLE aptitude_performance (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	quantitative_score FLOAT, 
	logical_reasoning_score FLOAT, 
	verbal_communication_score FLOAT, 
	mock_interview_score FLOAT, 
	overall_aptitude_score FLOAT, 
	tests_completed_count INTEGER, 
	percentile FLOAT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (student_profile_id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: career_roadmaps
CREATE TABLE career_roadmaps (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	job_role_id INTEGER, 
	title VARCHAR(200) NOT NULL, 
	target_timeline_weeks INTEGER, 
	current_week INTEGER, 
	total_milestones INTEGER, 
	completed_milestones INTEGER, 
	roadmap_data JSON NOT NULL, 
	status VARCHAR(30), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE, 
	FOREIGN KEY(job_role_id) REFERENCES job_roles (id) ON DELETE SET NULL
);

-- Table: certifications
CREATE TABLE certifications (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	issuing_organization VARCHAR(150) NOT NULL, 
	credential_id VARCHAR(100), 
	credential_url VARCHAR(255), 
	issue_date DATE, 
	expiry_date DATE, 
	skills_covered JSON, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: coding_performance
CREATE TABLE coding_performance (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	coding_skill_score FLOAT, 
	leetcode_solved_count INTEGER, 
	leetcode_easy INTEGER, 
	leetcode_medium INTEGER, 
	leetcode_hard INTEGER, 
	codeforces_rating INTEGER, 
	hackerrank_stars INTEGER, 
	github_repos_count INTEGER, 
	hackathons_participated INTEGER, 
	languages_breakdown JSON, 
	last_synced_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (student_profile_id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: digital_career_twin
CREATE TABLE digital_career_twin (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	twin_name VARCHAR(100), 
	twin_version INTEGER, 
	coding_score FLOAT, 
	aptitude_score FLOAT, 
	communication_score FLOAT, 
	logical_score FLOAT, 
	leadership_score FLOAT, 
	project_score FLOAT, 
	overall_twin_score FLOAT, 
	benchmark_percentile FLOAT, 
	projected_placement_chance FLOAT, 
	projected_salary_lpa FLOAT, 
	simulation_state JSON, 
	radar_history JSON, 
	last_simulated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (student_profile_id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: internships
CREATE TABLE internships (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	company_name VARCHAR(150) NOT NULL, 
	role VARCHAR(100) NOT NULL, 
	domain VARCHAR(100), 
	location VARCHAR(100), 
	duration_months INTEGER, 
	start_date DATE, 
	end_date DATE, 
	description TEXT, 
	stipend_monthly FLOAT, 
	is_completed BOOLEAN, 
	certificate_url VARCHAR(255), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: job_requirements
CREATE TABLE job_requirements (
	id SERIAL NOT NULL, 
	job_role_id INTEGER NOT NULL, 
	min_cgpa FLOAT, 
	max_active_backlogs INTEGER, 
	eligible_branches JSON, 
	must_have_skills JSON NOT NULL, 
	good_to_have_skills JSON, 
	min_internships_count INTEGER, 
	min_projects_count INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (job_role_id), 
	FOREIGN KEY(job_role_id) REFERENCES job_roles (id) ON DELETE CASCADE
);

-- Table: placement_readiness
CREATE TABLE placement_readiness (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	readiness_score FLOAT NOT NULL, 
	predicted_status VARCHAR(30) NOT NULL, 
	placement_probability FLOAT NOT NULL, 
	predicted_salary_min_lpa FLOAT, 
	predicted_salary_max_lpa FLOAT, 
	confidence_score FLOAT, 
	top_positive_factors JSON, 
	top_risk_factors JSON, 
	model_version VARCHAR(50), 
	assessed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: progress_tracking
CREATE TABLE progress_tracking (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	category VARCHAR(50) NOT NULL, 
	item_title VARCHAR(200) NOT NULL, 
	status VARCHAR(30), 
	completion_percentage FLOAT, 
	score_obtained FLOAT, 
	notes TEXT, 
	logged_date DATE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: projects
CREATE TABLE projects (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	domain VARCHAR(100), 
	tech_stack JSON, 
	github_url VARCHAR(255), 
	live_demo_url VARCHAR(255), 
	complexity_level VARCHAR(30), 
	is_featured BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: recommendations
CREATE TABLE recommendations (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	course_id INTEGER, 
	type VARCHAR(50) NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	priority VARCHAR(20), 
	action_url VARCHAR(500), 
	is_completed BOOLEAN, 
	is_dismissed BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE, 
	FOREIGN KEY(course_id) REFERENCES courses (id) ON DELETE SET NULL
);

-- Table: resumes
CREATE TABLE resumes (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	file_name VARCHAR(255) NOT NULL, 
	file_path VARCHAR(500) NOT NULL, 
	file_size_bytes INTEGER, 
	parsed_text TEXT, 
	ats_score FLOAT, 
	extracted_skills JSON, 
	extracted_experience_years FLOAT, 
	formatting_score FLOAT, 
	strengths JSON, 
	improvements_suggested JSON, 
	uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE
);

-- Table: skill_gap_results
CREATE TABLE skill_gap_results (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	job_role_id INTEGER NOT NULL, 
	match_percentage FLOAT NOT NULL, 
	matching_skills JSON, 
	missing_critical_skills JSON, 
	missing_secondary_skills JSON, 
	readiness_tier VARCHAR(50), 
	analysis_notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE, 
	FOREIGN KEY(job_role_id) REFERENCES job_roles (id) ON DELETE CASCADE
);

-- Table: student_skills
CREATE TABLE student_skills (
	id SERIAL NOT NULL, 
	student_profile_id INTEGER NOT NULL, 
	skill_id INTEGER NOT NULL, 
	proficiency_level VARCHAR(30) NOT NULL, 
	proficiency_score FLOAT, 
	years_of_experience FLOAT, 
	verified_by VARCHAR(50), 
	last_practiced DATE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_student_skill UNIQUE (student_profile_id, skill_id), 
	FOREIGN KEY(student_profile_id) REFERENCES student_profiles (id) ON DELETE CASCADE, 
	FOREIGN KEY(skill_id) REFERENCES skills (id) ON DELETE CASCADE
);

