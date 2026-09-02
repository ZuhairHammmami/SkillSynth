-- 003_reduced_schema.sql
-- Canonical SQLite DDL for SkillSynth reduced domain schema (15 tables, strict 3NF).
-- Truth source: SQLAlchemy ORM metadata (src/backend/entities/{identity,catalog,
-- learning,assessment,engagement}.py).
-- Verified against Base.metadata.create_all by tools/verify_schema.py.
--
-- Documented exceptions to strict 3NF (JSON bridges):
--   assessment_questions.options, path_steps.resource_ids, path_steps.assessment_ids,
--   activity_log.data, skills.topics, path_steps.learning_objectives,
--   user_skills.weak_points

PRAGMA foreign_keys=ON;

-- ─── Identity ───────────────────────────────────────────────────

CREATE TABLE users (
	id INTEGER NOT NULL,
	email VARCHAR NOT NULL,
	hashed_password VARCHAR NOT NULL,
	full_name VARCHAR,
	is_admin BOOLEAN NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (email)
);
CREATE INDEX ix_users_id ON users (id);

-- ─── Catalog ────────────────────────────────────────────────────

CREATE TABLE categories (
	id INTEGER NOT NULL,
	name VARCHAR(100) NOT NULL,
	description VARCHAR,
	parent_id INTEGER,
	PRIMARY KEY (id),
	UNIQUE (name),
	FOREIGN KEY(parent_id) REFERENCES categories (id) ON DELETE SET NULL
);
CREATE INDEX ix_categories_id ON categories (id);
CREATE INDEX idx_categories_parent_id ON categories (parent_id);

CREATE TABLE skills (
	id INTEGER NOT NULL,
	name VARCHAR(100) NOT NULL,
	description TEXT,
	difficulty_level INTEGER NOT NULL DEFAULT 0,
	estimated_hours REAL NOT NULL DEFAULT 0.0,
	icon VARCHAR,
	color VARCHAR,
	category_id INTEGER,
	topics JSON,  -- documented JSON exception: list of topic strings
	PRIMARY KEY (id),
	UNIQUE (name),
	CONSTRAINT chk_difficulty CHECK(difficulty_level >= 0 AND difficulty_level <= 10),
	CONSTRAINT chk_hours CHECK(estimated_hours >= 0),
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE SET NULL
);
CREATE INDEX ix_skills_id ON skills (id);
CREATE INDEX idx_skills_category_id ON skills (category_id);

CREATE TABLE skill_prerequisites (
	skill_id INTEGER NOT NULL,
	prerequisite_id INTEGER NOT NULL,
	PRIMARY KEY (skill_id, prerequisite_id),
	FOREIGN KEY(skill_id) REFERENCES skills (id) ON DELETE CASCADE,
	FOREIGN KEY(prerequisite_id) REFERENCES skills (id) ON DELETE CASCADE
);
CREATE INDEX idx_skill_prerequisites_prerequisite_id ON skill_prerequisites (prerequisite_id);

CREATE TABLE job_roles (
	id INTEGER NOT NULL,
	title VARCHAR(150) NOT NULL,
	description TEXT,
	career_field VARCHAR(100),
	PRIMARY KEY (id),
	UNIQUE (title)
);
CREATE INDEX ix_job_roles_id ON job_roles (id);

CREATE TABLE job_role_skills (
	job_role_id INTEGER NOT NULL,
	skill_id INTEGER NOT NULL,
	PRIMARY KEY (job_role_id, skill_id),
	FOREIGN KEY(job_role_id) REFERENCES job_roles (id) ON DELETE CASCADE,
	FOREIGN KEY(skill_id) REFERENCES skills (id) ON DELETE CASCADE
);
CREATE INDEX idx_job_role_skills_skill_id ON job_role_skills (skill_id);

CREATE TABLE resources (
	id INTEGER NOT NULL,
	title VARCHAR(200) NOT NULL,
	url VARCHAR(2000) NOT NULL,
	type VARCHAR(50) NOT NULL,
	language VARCHAR(10),
	is_free BOOLEAN,
	is_official BOOLEAN,
	author_or_platform VARCHAR(200),
	skill_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(skill_id) REFERENCES skills (id) ON DELETE SET NULL
);
CREATE INDEX ix_resources_id ON resources (id);
CREATE INDEX idx_resources_skill_id ON resources (skill_id);

-- ─── Assessment ─────────────────────────────────────────────────

CREATE TABLE assessments (
	id INTEGER NOT NULL,
	skill_id INTEGER,
	title VARCHAR(200) NOT NULL,
	description TEXT,
	pass_score INTEGER,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT chk_pass_score CHECK(pass_score >= 0 AND pass_score <= 100),
	FOREIGN KEY(skill_id) REFERENCES skills (id) ON DELETE SET NULL
);
CREATE INDEX ix_assessments_id ON assessments (id);
CREATE INDEX idx_assessments_skill_id ON assessments (skill_id);

CREATE TABLE assessment_questions (
	id INTEGER NOT NULL,
	assessment_id INTEGER NOT NULL,
	position INTEGER NOT NULL,
	prompt TEXT NOT NULL,
	options JSON NOT NULL,
	correct_index INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT chk_correct CHECK(correct_index >= 0),
	FOREIGN KEY(assessment_id) REFERENCES assessments (id) ON DELETE CASCADE
);
CREATE INDEX ix_assessment_questions_id ON assessment_questions (id);
CREATE INDEX idx_assessment_questions_assessment_id ON assessment_questions (assessment_id);

CREATE TABLE assessment_results (
	id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	assessment_id INTEGER NOT NULL,
	score INTEGER NOT NULL,
	passed BOOLEAN NOT NULL,
	completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
	FOREIGN KEY(assessment_id) REFERENCES assessments (id) ON DELETE CASCADE
);
CREATE INDEX ix_assessment_results_id ON assessment_results (id);
CREATE INDEX idx_assessment_results_user_id ON assessment_results (user_id);
CREATE INDEX idx_assessment_results_assessment_id ON assessment_results (assessment_id);
CREATE INDEX idx_assessment_results_user_completed ON assessment_results(user_id, completed_at);

-- ─── Learning ───────────────────────────────────────────────────

CREATE TABLE user_skills (
	user_id INTEGER NOT NULL,
	skill_id INTEGER NOT NULL,
	proficiency_level INTEGER NOT NULL DEFAULT 0,
	last_assessed_at TIMESTAMP,
	weak_points JSON,  -- documented JSON exception: list of weak-point strings
	PRIMARY KEY (user_id, skill_id),
	CONSTRAINT chk_proficiency CHECK(proficiency_level >= 0 AND proficiency_level <= 5),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
	FOREIGN KEY(skill_id) REFERENCES skills (id) ON DELETE CASCADE
);
CREATE INDEX idx_user_skills_skill_id ON user_skills (skill_id);

CREATE TABLE paths (
	id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	title VARCHAR(200) NOT NULL,
	description TEXT,
	target_role VARCHAR(150),
	status VARCHAR(20),
	total_estimated_hours INTEGER NOT NULL,
	total_estimated_weeks INTEGER NOT NULL,
	deleted_at TIMESTAMP,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_paths_id ON paths (id);
CREATE INDEX idx_paths_user_id ON paths (user_id);
CREATE INDEX idx_paths_user_status ON paths(user_id, status);

CREATE TABLE path_steps (
	id INTEGER NOT NULL,
	path_id INTEGER NOT NULL,
	skill_id INTEGER,
	position INTEGER NOT NULL,
	title VARCHAR(200) NOT NULL,
	description TEXT,
	estimated_hours INTEGER,
	resource_ids JSON,
	assessment_ids JSON,
	learning_objectives JSON,  -- documented JSON exception: list of objective strings
	selected_level INTEGER NOT NULL DEFAULT 0,
	current_level INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY (id),
	CONSTRAINT chk_selected_level CHECK(selected_level >= 0 AND selected_level <= 5),
	CONSTRAINT chk_step_level CHECK(current_level >= 0 AND current_level <= 5),
	FOREIGN KEY(path_id) REFERENCES paths (id) ON DELETE CASCADE,
	FOREIGN KEY(skill_id) REFERENCES skills (id) ON DELETE SET NULL
);
CREATE INDEX ix_path_steps_id ON path_steps (id);
CREATE INDEX idx_path_steps_path_id ON path_steps (path_id);
CREATE INDEX idx_path_steps_skill_id ON path_steps (skill_id);

CREATE TABLE step_progress (
	user_id INTEGER NOT NULL,
	step_id INTEGER NOT NULL,
	completed_at TIMESTAMP,
	score INTEGER,
	PRIMARY KEY (user_id, step_id),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE,
	FOREIGN KEY(step_id) REFERENCES path_steps (id) ON DELETE CASCADE
);
CREATE INDEX idx_step_progress_step_id ON step_progress (step_id);
CREATE INDEX idx_step_progress_user_step ON step_progress(user_id, step_id);

-- ─── Engagement ─────────────────────────────────────────────────

CREATE TABLE activity_log (
	id INTEGER NOT NULL,
	user_id INTEGER,
	category VARCHAR(20) NOT NULL,
	action VARCHAR(100) NOT NULL,
	entity_type VARCHAR(50),
	entity_id VARCHAR(50),
	data JSON,
	ip_address VARCHAR(45),
	user_agent VARCHAR(255),
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_activity_log_id ON activity_log (id);
CREATE INDEX idx_activity_log_user_id ON activity_log (user_id);
CREATE INDEX idx_activity_log_category ON activity_log(category);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);
