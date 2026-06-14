-- AEIS Database Schema Migration
-- Supabase PostgreSQL

CREATE TABLE IF NOT EXISTS concepts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  label VARCHAR(255) NOT NULL,
  confidence_score NUMERIC(3,2) NOT NULL CHECK (confidence_score > 0.7),
  source_type VARCHAR(50) NOT NULL,
  source_url TEXT,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reliability_score NUMERIC(3,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS concept_prerequisites (
  concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  prerequisite_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  PRIMARY KEY (concept_id, prerequisite_id),
  CHECK (concept_id != prerequisite_id)
);

CREATE TABLE IF NOT EXISTS engineering_projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  phase VARCHAR(50) NOT NULL CHECK (phase IN ('MVP', 'Production', 'Scalable')),
  start_date TIMESTAMP,
  end_date TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_concepts (
  project_id UUID NOT NULL REFERENCES engineering_projects(id) ON DELETE CASCADE,
  concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  PRIMARY KEY (project_id, concept_id)
);

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_mastery (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  current_node_id UUID REFERENCES concepts(id),
  path_history UUID[] DEFAULT ARRAY[]::UUID[],
  allowed_paths UUID[] DEFAULT ARRAY[]::UUID[],
  custom_skill_overrides JSONB DEFAULT '{}'::JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_concepts_confidence ON concepts(confidence_score);
CREATE INDEX IF NOT EXISTS idx_user_mastery_user_id ON user_mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_phase ON engineering_projects(phase);
CREATE INDEX IF NOT EXISTS idx_concept_prerequisites ON concept_prerequisites(concept_id);

-- Enable Row Level Security (RLS) for future auth integration
ALTER TABLE concepts ENABLE ROW LEVEL SECURITY;
ALTER TABLE engineering_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_mastery ENABLE ROW LEVEL SECURITY;
