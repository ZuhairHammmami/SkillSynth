-- user_path table - stores user's learning paths
CREATE TABLE IF NOT EXISTS user_path (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  nodes JSONB DEFAULT '[]'::JSONB,
  current_node_id UUID,
  progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_path_user_id ON user_path(user_id);
CREATE INDEX idx_user_path_progress ON user_path(progress);

ALTER TABLE user_path ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own paths"
  ON user_path FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own paths"
  ON user_path FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own paths"
  ON user_path FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own paths"
  ON user_path FOR DELETE
  USING (auth.uid() = user_id);