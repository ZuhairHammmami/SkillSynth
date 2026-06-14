/**
 * src/migrations/004_phase_4_5_vector_search.sql
 * 
 * Phase 4.5: Vector Search & Intelligent Discovery
 * 
 * New entities and tables:
 * 1. Enable pgvector extension
 * 2. concept_embeddings - Vector embeddings for semantic search
 * 3. embedding_metadata - Tracks embedding generation metadata
 * 4. vector_search_queries - Logs search queries for analytics
 */

-- ============================================================================
-- ENABLE PGVECTOR EXTENSION
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- CONCEPT EMBEDDINGS TABLE
-- ============================================================================

-- Store embeddings for concepts, projects, and explanations
CREATE TABLE IF NOT EXISTS concept_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Reference to source entity
  concept_id UUID NOT NULL,
  entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('concept', 'project', 'explanation')),
  
  -- Content being embedded
  content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('title', 'description', 'full')),
  content TEXT NOT NULL,
  
  -- Vector embedding (3072 dimensions for text-embedding-3-small)
  embedding vector(1536) NOT NULL,
  
  -- Metadata
  provider VARCHAR(20) NOT NULL CHECK (provider IN ('openai', 'local')),
  model_used VARCHAR(100),
  
  -- Tracking
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
  UNIQUE(concept_id, entity_type, content_type, provider)
);

-- Create indexes for efficient vector search
CREATE INDEX idx_concept_embeddings_concept_id ON concept_embeddings(concept_id);
CREATE INDEX idx_concept_embeddings_entity_type ON concept_embeddings(entity_type);
CREATE INDEX idx_concept_embeddings_created_at ON concept_embeddings(created_at DESC);

-- Create vector similarity search index (IVFFlat with 100 lists)
CREATE INDEX idx_concept_embeddings_vector ON concept_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- RLS Policy: Everyone can read embeddings for discovery
ALTER TABLE concept_embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read concept embeddings"
  ON concept_embeddings FOR SELECT
  USING (true);

-- ============================================================================
-- EMBEDDING METADATA TABLE
-- ============================================================================

-- Track embedding generation statistics
CREATE TABLE IF NOT EXISTS embedding_metadata (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Batch info
  batch_id UUID NOT NULL,
  concept_count INTEGER NOT NULL,
  
  -- Timing and costs
  total_tokens INTEGER,
  total_cost_usd DECIMAL(10, 6),
  generation_time_ms INTEGER,
  
  -- Provider info
  provider VARCHAR(20) NOT NULL CHECK (provider IN ('openai', 'local')),
  model_used VARCHAR(100),
  
  -- Status
  status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  error_message TEXT,
  
  -- Timestamps
  started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP WITH TIME ZONE,
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_embedding_metadata_batch_id ON embedding_metadata(batch_id);
CREATE INDEX idx_embedding_metadata_status ON embedding_metadata(status);
CREATE INDEX idx_embedding_metadata_completed_at ON embedding_metadata(completed_at DESC);

-- ============================================================================
-- VECTOR SEARCH QUERIES TABLE
-- ============================================================================

-- Log all vector search queries for analytics and debugging
CREATE TABLE IF NOT EXISTS vector_search_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID,
  query_text TEXT NOT NULL,
  
  -- Search parameters
  entity_types VARCHAR(255), -- CSV list of types: concept,project,explanation
  limit_results INTEGER DEFAULT 5,
  
  -- Results
  result_count INTEGER,
  top_result_id UUID,
  top_result_score DECIMAL(5, 4),
  
  -- Performance
  search_time_ms INTEGER,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE SET NULL,
  FOREIGN KEY (top_result_id) REFERENCES concepts(id) ON DELETE SET NULL
);

CREATE INDEX idx_vector_search_queries_user_id ON vector_search_queries(user_id);
CREATE INDEX idx_vector_search_queries_created_at ON vector_search_queries(created_at DESC);

-- RLS Policy: Users can view their own searches, admins can view all
ALTER TABLE vector_search_queries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own searches"
  ON vector_search_queries FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all searches"
  ON vector_search_queries FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM user_mastery um
      WHERE um.user_id = auth.uid() AND um.custom_skill_overrides->'admin_privileges' = 'true'
    )
  );

-- ============================================================================
-- VECTOR SEARCH FUNCTION (PostgreSQL)
-- ============================================================================

-- Perform semantic similarity search using cosine distance
CREATE OR REPLACE FUNCTION search_concepts_by_embedding(
  search_embedding vector,
  entity_type_filter VARCHAR DEFAULT NULL,
  result_limit INTEGER DEFAULT 5
)
RETURNS TABLE(
  concept_id UUID,
  entity_type VARCHAR,
  content TEXT,
  similarity DECIMAL,
  model_used VARCHAR
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    ce.concept_id,
    ce.entity_type,
    ce.content,
    (1 - (ce.embedding <=> search_embedding))::DECIMAL AS similarity,
    ce.model_used
  FROM concept_embeddings ce
  WHERE (entity_type_filter IS NULL OR ce.entity_type = entity_type_filter)
  ORDER BY ce.embedding <=> search_embedding
  LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================

-- Top searched concepts
CREATE OR REPLACE VIEW top_searched_concepts AS
SELECT 
  c.id,
  c.title,
  COUNT(vsq.id) as search_count,
  AVG(vsq.top_result_score::FLOAT) as avg_relevance
FROM concepts c
LEFT JOIN vector_search_queries vsq ON c.id = vsq.top_result_id
GROUP BY c.id, c.title
ORDER BY search_count DESC
LIMIT 20;

-- Embedding status overview
CREATE OR REPLACE VIEW embedding_generation_stats AS
SELECT 
  provider,
  COUNT(DISTINCT batch_id) as batch_count,
  SUM(concept_count) as total_concepts,
  SUM(total_tokens) as total_tokens,
  SUM(total_cost_usd) as total_cost,
  AVG(generation_time_ms) as avg_generation_time_ms,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_batches,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_batches
FROM embedding_metadata
GROUP BY provider;
