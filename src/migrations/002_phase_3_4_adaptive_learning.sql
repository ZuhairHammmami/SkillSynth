-- Phase 3.4: Advanced Adaptive Learning & Mastery Validation
-- Supabase PostgreSQL Migration

-- Assessment Results Table: Tracks quiz performance for each concept
CREATE TABLE IF NOT EXISTS assessment_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  score NUMERIC(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
  total_questions INTEGER NOT NULL DEFAULT 1,
  correct_answers INTEGER NOT NULL,
  attempt_number INTEGER NOT NULL DEFAULT 1,
  passed BOOLEAN NOT NULL DEFAULT FALSE,
  time_spent_seconds INTEGER,
  answers JSONB DEFAULT '{}'::JSONB, -- Store detailed answers for analysis
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, concept_id, attempt_number)
);

-- User Stuck Tracking: Monitor time spent on a single node without completion
CREATE TABLE IF NOT EXISTS user_stuck_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  node_start_time TIMESTAMP NOT NULL,
  hours_elapsed NUMERIC(5,1) DEFAULT 0,
  intervention_triggered BOOLEAN DEFAULT FALSE,
  intervention_triggered_at TIMESTAMP,
  intervention_type VARCHAR(50) CHECK (intervention_type IN ('learning_intervention', 'skip_option', 'alternative_path')),
  simplified_subpath UUID[] DEFAULT ARRAY[]::UUID[], -- Alternative path nodes
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, concept_id)
);

-- Alternative Explanations Cache: Store LLM-generated explanations for concepts
CREATE TABLE IF NOT EXISTS alternative_explanations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  generated_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL, -- Null = system-generated
  explanation_text TEXT NOT NULL,
  difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
  prerequisites_considered UUID[] DEFAULT ARRAY[]::UUID[],
  quality_score NUMERIC(3,2), -- Tracks explanation effectiveness (0-1)
  model_used VARCHAR(50) DEFAULT 'openai-gpt-4', -- Track which model generated this
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skill Gaps Table: Track which prerequisites are weak (low reliability)
CREATE TABLE IF NOT EXISTS skill_gaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  weak_skill_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  blocked_advanced_skills UUID[] DEFAULT ARRAY[]::UUID[], -- Skills blocked by this weakness
  reliability_score NUMERIC(3,2) NOT NULL,
  last_assessment_date TIMESTAMP,
  recommendation_status VARCHAR(50) DEFAULT 'pending' CHECK (recommendation_status IN ('pending', 'recommended', 'in_progress', 'resolved')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, weak_skill_id)
);

-- Learning Interventions Log: Audit trail of all interventions triggered
CREATE TABLE IF NOT EXISTS learning_interventions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
  intervention_type VARCHAR(50) NOT NULL CHECK (intervention_type IN ('learning_intervention', 'skip_option', 'alternative_path')),
  trigger_reason VARCHAR(50) NOT NULL CHECK (trigger_reason IN ('stuck_48h', 'repeated_failures', 'skill_gap')),
  hours_spent NUMERIC(5,1),
  failed_attempts INTEGER,
  intervention_accepted BOOLEAN,
  action_taken VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_assessment_results_user_concept ON assessment_results(user_id, concept_id);
CREATE INDEX IF NOT EXISTS idx_assessment_results_passed ON assessment_results(user_id, passed);
CREATE INDEX IF NOT EXISTS idx_assessment_results_created ON assessment_results(created_at);
CREATE INDEX IF NOT EXISTS idx_user_stuck_tracking_user ON user_stuck_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stuck_tracking_intervention ON user_stuck_tracking(user_id, intervention_triggered);
CREATE INDEX IF NOT EXISTS idx_skill_gaps_user ON skill_gaps(user_id);
CREATE INDEX IF NOT EXISTS idx_skill_gaps_recommendation ON skill_gaps(user_id, recommendation_status);
CREATE INDEX IF NOT EXISTS idx_alternative_explanations_concept ON alternative_explanations(concept_id);
CREATE INDEX IF NOT EXISTS idx_learning_interventions_user ON learning_interventions(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_interventions_trigger ON learning_interventions(user_id, trigger_reason);

-- Enable RLS for new tables
ALTER TABLE assessment_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_stuck_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE alternative_explanations ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_interventions ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own assessment results
CREATE POLICY "Users can view their own assessments" ON assessment_results
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own assessment results" ON assessment_results
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can only see their own stuck tracking
CREATE POLICY "Users can view their own stuck tracking" ON user_stuck_tracking
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own stuck tracking" ON user_stuck_tracking
  FOR UPDATE USING (auth.uid() = user_id);

-- RLS Policy: Skill gaps are public for recommendations but tied to user progress
CREATE POLICY "Users can view their own skill gaps" ON skill_gaps
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own skill gaps" ON skill_gaps
  FOR INSERT WITH CHECK (auth.uid() = user_id);
