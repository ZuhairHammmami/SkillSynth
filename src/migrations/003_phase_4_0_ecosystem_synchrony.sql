/**
 * src/migrations/003_phase_4_0_ecosystem_synchrony.sql
 * 
 * Phase 4.0: Ecosystem Synchrony - Database Schema
 * 
 * New entities and tables:
 * 1. project_node_requirements - Bridge table linking projects to knowledge nodes
 * 2. project_submissions - Tracks user submissions for project milestones
 * 3. github_validation_cache - Cache GitHub URL validation results
 * 4. community_templates - Community-curated learning paths
 * 5. shared_learning_paths - Public DAG shares with metrics
 */

-- ============================================================================
-- PROJECT NODE REQUIREMENTS (Bridge Table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS project_node_requirements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL,
  node_id UUID NOT NULL,
  required_milestone VARCHAR(50) NOT NULL CHECK (required_milestone IN ('design', 'implementation', 'testing', 'deployment', 'documentation')),
  passing_criteria TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (project_id) REFERENCES concepts(id) ON DELETE CASCADE,
  FOREIGN KEY (node_id) REFERENCES concepts(id) ON DELETE CASCADE,
  UNIQUE(project_id, node_id, required_milestone)
);

CREATE INDEX idx_project_node_requirements_project_id ON project_node_requirements(project_id);
CREATE INDEX idx_project_node_requirements_node_id ON project_node_requirements(node_id);

-- RLS Policy: Users can view project requirements for their learning paths
ALTER TABLE project_node_requirements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view project node requirements"
  ON project_node_requirements FOR SELECT
  USING (true); -- Public read access

-- ============================================================================
-- PROJECT SUBMISSIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS project_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  project_id UUID NOT NULL,
  node_id UUID NOT NULL,
  milestone VARCHAR(50) NOT NULL CHECK (milestone IN ('design', 'implementation', 'testing', 'deployment', 'documentation')),
  submission_type VARCHAR(50) NOT NULL CHECK (submission_type IN ('file_upload', 'github_url', 'code_snippet', 'demo_link')),
  
  -- Submission data (mutually exclusive)
  file_url TEXT,
  github_url TEXT,
  code_snippet TEXT,
  demo_link TEXT,
  
  -- Metadata
  description TEXT,
  
  -- Review status
  passed BOOLEAN,
  reviewed_at TIMESTAMP WITH TIME ZONE,
  review_notes TEXT,
  
  -- Timestamps
  submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
  FOREIGN KEY (project_id) REFERENCES concepts(id) ON DELETE CASCADE,
  FOREIGN KEY (node_id) REFERENCES concepts(id) ON DELETE CASCADE
);

CREATE INDEX idx_project_submissions_user_id ON project_submissions(user_id);
CREATE INDEX idx_project_submissions_project_id ON project_submissions(project_id);
CREATE INDEX idx_project_submissions_node_id ON project_submissions(node_id);
CREATE INDEX idx_project_submissions_milestone ON project_submissions(milestone);
CREATE INDEX idx_project_submissions_status ON project_submissions(passed);
CREATE INDEX idx_project_submissions_submitted_at ON project_submissions(submitted_at DESC);

-- RLS Policy: Users can only view/insert their own submissions
ALTER TABLE project_submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own submissions"
  ON project_submissions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own submissions"
  ON project_submissions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can review all submissions"
  ON project_submissions FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM user_mastery um
      WHERE um.user_id = auth.uid() AND um.custom_skill_overrides->'admin_privileges' = 'true'
    )
  );

-- ============================================================================
-- GITHUB URL VALIDATION CACHE
-- ============================================================================
CREATE TABLE IF NOT EXISTS github_validation_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  github_url TEXT NOT NULL UNIQUE,
  owner VARCHAR(255),
  repo VARCHAR(255),
  branch VARCHAR(255) DEFAULT 'main',
  is_valid BOOLEAN NOT NULL,
  status_code INTEGER,
  validation_error TEXT,
  last_checked TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
  
  CONSTRAINT valid_github_url CHECK (github_url LIKE '%github.com%')
);

CREATE INDEX idx_github_validation_cache_url ON github_validation_cache(github_url);
CREATE INDEX idx_github_validation_cache_expires_at ON github_validation_cache(expires_at);

-- Auto-cleanup expired cache entries (optional, depends on maintenance strategy)
-- DELETE FROM github_validation_cache WHERE expires_at < CURRENT_TIMESTAMP;

-- ============================================================================
-- COMMUNITY TEMPLATES (Phase 4.0: Social Mastery Graphs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS community_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_by_user_id UUID NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  dag_structure JSONB NOT NULL,
  tag_array VARCHAR(50)[] DEFAULT '{}',
  target_role VARCHAR(100), -- e.g., "Backend Engineer", "Full Stack", "DevOps"
  difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
  estimated_hours INTEGER,
  
  -- Verification
  verified BOOLEAN DEFAULT false,
  verified_by_admin UUID,
  verified_at TIMESTAMP WITH TIME ZONE,
  verification_notes TEXT,
  
  -- Stats
  clone_count INTEGER DEFAULT 0,
  rating DECIMAL(3, 2) CHECK (rating >= 0 AND rating <= 5),
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (created_by_user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
  FOREIGN KEY (verified_by_admin) REFERENCES auth.users(id) ON DELETE SET NULL
);

CREATE INDEX idx_community_templates_verified ON community_templates(verified);
CREATE INDEX idx_community_templates_difficulty ON community_templates(difficulty_level);
CREATE INDEX idx_community_templates_rating ON community_templates(rating DESC);
CREATE INDEX idx_community_templates_created_at ON community_templates(created_at DESC);

-- RLS Policy: Anyone can view verified templates, creators can view/edit their own
ALTER TABLE community_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view verified templates"
  ON community_templates FOR SELECT
  USING (verified = true OR auth.uid() = created_by_user_id);

CREATE POLICY "Users can create templates"
  ON community_templates FOR INSERT
  WITH CHECK (auth.uid() = created_by_user_id);

CREATE POLICY "Users can update their own templates"
  ON community_templates FOR UPDATE
  USING (auth.uid() = created_by_user_id);

-- ============================================================================
-- SHARED LEARNING PATHS (Public DAGs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS shared_learning_paths (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  path_id UUID NOT NULL,
  share_token VARCHAR(64) NOT NULL UNIQUE, -- Random token for public link
  is_public BOOLEAN DEFAULT true,
  is_read_only BOOLEAN DEFAULT true,
  password_protected BOOLEAN DEFAULT false,
  password_hash VARCHAR(255),
  
  -- Tracking
  view_count INTEGER DEFAULT 0,
  clone_count INTEGER DEFAULT 0,
  last_viewed TIMESTAMP WITH TIME ZONE,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
  FOREIGN KEY (path_id) REFERENCES user_path(id) ON DELETE CASCADE
);

CREATE INDEX idx_shared_learning_paths_user_id ON shared_learning_paths(user_id);
CREATE INDEX idx_shared_learning_paths_share_token ON shared_learning_paths(share_token);
CREATE INDEX idx_shared_learning_paths_is_public ON shared_learning_paths(is_public);
CREATE INDEX idx_shared_learning_paths_view_count ON shared_learning_paths(view_count DESC);

-- RLS Policy: Owners can manage shares, public shares are readable by all
ALTER TABLE shared_learning_paths ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Path owners can manage shares"
  ON shared_learning_paths FOR ALL
  USING (auth.uid() = user_id);

CREATE POLICY "Anyone can view public shares"
  ON shared_learning_paths FOR SELECT
  USING (is_public = true);

-- ============================================================================
-- PATH CLONES TRACKING (Social Metrics)
-- ============================================================================
CREATE TABLE IF NOT EXISTS path_clones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  original_path_id UUID NOT NULL,
  cloned_by_user_id UUID NOT NULL,
  cloned_path_id UUID NOT NULL,
  clone_source VARCHAR(50) NOT NULL CHECK (clone_source IN ('community_template', 'shared_path')),
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (original_path_id) REFERENCES user_path(id) ON DELETE CASCADE,
  FOREIGN KEY (cloned_by_user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
  FOREIGN KEY (cloned_path_id) REFERENCES user_path(id) ON DELETE CASCADE
);

CREATE INDEX idx_path_clones_original_path_id ON path_clones(original_path_id);
CREATE INDEX idx_path_clones_cloned_by_user_id ON path_clones(cloned_by_user_id);
CREATE INDEX idx_path_clones_clone_source ON path_clones(clone_source);
CREATE INDEX idx_path_clones_created_at ON path_clones(created_at DESC);

-- RLS Policy: Users can view clones of their paths, users can insert their own clones
ALTER TABLE path_clones ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view clones of their paths"
  ON path_clones FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM user_path up
      WHERE up.id = original_path_id AND up.user_id = auth.uid()
    )
    OR cloned_by_user_id = auth.uid()
  );

CREATE POLICY "Users can track their clones"
  ON path_clones FOR INSERT
  WITH CHECK (cloned_by_user_id = auth.uid());

-- ============================================================================
-- ALTERNATIVE EXPLANATIONS ENHANCEMENTS (Phase 4.0)
-- ============================================================================
-- Add provider and cost tracking to alternative_explanations table
-- Note: This assumes alternative_explanations table exists from Phase 3.4

-- Add new columns if they don't exist (idempotent)
ALTER TABLE IF EXISTS alternative_explanations
ADD COLUMN IF NOT EXISTS provider VARCHAR(20) DEFAULT 'openai' CHECK (provider IN ('openai', 'local')),
ADD COLUMN IF NOT EXISTS generation_time_ms INTEGER,
ADD COLUMN IF NOT EXISTS cost_estimate DECIMAL(10, 6);

-- Create index for provider filtering (cost analysis, provider statistics)
CREATE INDEX IF NOT EXISTS idx_alternative_explanations_provider ON alternative_explanations(provider);
CREATE INDEX IF NOT EXISTS idx_alternative_explanations_cost ON alternative_explanations(cost_estimate DESC);

-- ============================================================================
-- LLM USAGE ANALYTICS (Phase 4.0)
-- ============================================================================
CREATE TABLE IF NOT EXISTS llm_usage_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  provider VARCHAR(20) NOT NULL CHECK (provider IN ('openai', 'local')),
  operation_type VARCHAR(50) NOT NULL CHECK (operation_type IN ('explanation', 'quiz', 'assessment')),
  model_used VARCHAR(100),
  generation_time_ms INTEGER,
  tokens_used INTEGER,
  cost_usd DECIMAL(10, 6),
  success BOOLEAN DEFAULT true,
  error_message TEXT,
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL
);

CREATE INDEX idx_llm_usage_analytics_provider ON llm_usage_analytics(provider);
CREATE INDEX idx_llm_usage_analytics_user_id ON llm_usage_analytics(user_id);
CREATE INDEX idx_llm_usage_analytics_created_at ON llm_usage_analytics(created_at DESC);

-- RLS Policy: Users can view their own usage analytics, admins can view all
ALTER TABLE llm_usage_analytics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own LLM usage"
  ON llm_usage_analytics FOR SELECT
  USING (auth.uid() = user_id OR auth.uid() IN (
    SELECT user_id FROM user_mastery WHERE custom_skill_overrides->'admin_privileges' = 'true'
  ));
