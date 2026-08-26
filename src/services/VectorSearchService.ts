/**
 * src/services/VectorSearchService.ts
 * 
 * Vector Search Service (Phase 4.5)
 * Semantic search using embeddings with hybrid provider strategy
 * 
 * Features:
 * - Embedding generation using HybridLLMProvider (OpenAI or local)
 * - Cosine similarity search via PostgreSQL pgvector
 * - Batch embedding generation for concepts
 * - Search result ranking and filtering
 * - Analytics logging
 */

import { HybridLLMProvider } from "./HybridLLMProvider";

interface EmbeddingResult {
  conceptId: string;
  embedding: number[];
  provider: "openai" | "local";
  modelUsed: string;
  tokensUsed?: number;
  costEstimate?: number;
}

interface SearchResult {
  conceptId: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  similarity: number; // 0-1, higher is more similar
  entityType: string;
}

interface SearchOptions {
  query: string;
  limit?: number;
  entityTypes?: string[];
  minSimilarity?: number;
  userId?: string;
}

interface DBQueryResult {
  rows: any[];
  error?: any;
}

interface DatabaseLike {
  query: (text: string, params?: any[]) => Promise<DBQueryResult>;
}

export class VectorSearchService {
  private db: DatabaseLike | null;
  private llmProvider: typeof HybridLLMProvider;

  constructor(db?: DatabaseLike) {
    this.db = db || null;
    this.llmProvider = HybridLLMProvider;
  }

  private async safeQuery(text: string, params?: any[]): Promise<DBQueryResult> {
    if (!this.db) {
      console.warn("[VectorSearchService] Database not configured, returning empty result");
      return { rows: [] };
    }
    try {
      return await this.db.query(text, params);
    } catch (error) {
      console.warn("[VectorSearchService] Database query failed:", error);
      return { rows: [], error };
    }
  }

  /**
   * Generate embedding for text using hybrid provider
   * Falls back from local to OpenAI if configured
   */
  async generateEmbedding(text: string): Promise<EmbeddingResult> {
    try {
      const startTime = Date.now();

      // Use OpenAI text-embedding-3-small (1536 dimensions)
      // This is the default as it's optimized for semantic search
      const response = await this.callEmbeddingAPI(text);

      const duration = Date.now() - startTime;

      return {
        conceptId: "", // Set by caller
        embedding: response.embedding,
        provider: response.provider,
        modelUsed: response.model,
        tokensUsed: response.tokens,
        costEstimate: response.cost,
      };
    } catch (error: any) {
      throw new Error(`Failed to generate embedding: ${error.message}`);
    }
  }

  /**
   * Call embedding API (OpenAI or local)
   */
  private async callEmbeddingAPI(
    text: string
  ): Promise<{
    embedding: number[];
    provider: "openai" | "local";
    model: string;
    tokens?: number;
    cost?: number;
  }> {
    const provider = process.env.LLM_PROVIDER || "hybrid";
    const useLocal = provider === "local" || provider === "hybrid";
    const useOpenAI = provider === "openai" || provider === "hybrid";

    // Try local first if hybrid or local
    if (useLocal) {
      try {
        return await this.generateEmbeddingLocal(text);
      } catch (error) {
        console.warn("Local embedding failed, falling back to OpenAI:", error);
        if (!useOpenAI) throw error;
      }
    }

    // Use OpenAI
    return await this.generateEmbeddingOpenAI(text);
  }

  /**
   * Generate embedding using local transformer (sentence-transformers)
   */
  private async generateEmbeddingLocal(text: string): Promise<{
    embedding: number[];
    provider: "local";
    model: string;
  }> {
    const model = process.env.OLLAMA_MODEL || "mistral";
    const baseUrl = process.env.OLLAMA_BASE_URL || "http://localhost:11434";

    // Ollama doesn't have native embedding endpoint, so we use sentence-transformers
    // Assuming a local service at port 8000 running sentence-transformers
    const embeddingServiceUrl = process.env.EMBEDDING_SERVICE_URL || "http://localhost:8000";

    const response = await fetch(`${embeddingServiceUrl}/embed`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, model: "all-MiniLM-L6-v2" }),
    });

    if (!response.ok) {
      throw new Error(`Embedding service error: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      embedding: data.embedding,
      provider: "local",
      model: "all-MiniLM-L6-v2",
    };
  }

  /**
   * Generate embedding using OpenAI text-embedding-3-small
   */
  private async generateEmbeddingOpenAI(text: string): Promise<{
    embedding: number[];
    provider: "openai";
    model: string;
    tokens: number;
    cost: number;
  }> {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error("OpenAI API key not configured");
    }

    const response = await fetch("https://api.openai.com/v1/embeddings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "text-embedding-3-small",
        input: text,
        encoding_format: "float",
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`OpenAI API error: ${error.error.message}`);
    }

    const data = await response.json();
    const embedding = data.data[0].embedding;
    const tokens = data.usage.total_tokens;

    // text-embedding-3-small costs $0.02 per 1M tokens
    const cost = (tokens / 1_000_000) * 0.02;

    return {
      embedding,
      provider: "openai",
      model: "text-embedding-3-small",
      tokens,
      cost,
    };
  }

  /**
   * Search for concepts using semantic similarity
   */
  async searchConcepts(options: SearchOptions): Promise<SearchResult[]> {
    const {
      query,
      limit = 5,
      entityTypes = ["concept"],
      minSimilarity = 0.5,
      userId,
    } = options;

    try {
      // Generate embedding for query
      const queryEmbedding = await this.generateEmbedding(query);

      // Log search query
      if (userId) {
        await this.logSearchQuery(userId, query, entityTypes, limit);
      }

      // Search in database using pgvector
      const results = await this.safeQuery(
        `
        SELECT 
          c.id as concept_id,
          c.title,
          c.description,
          c.difficulty,
          (1 - (ce.embedding <=> $1::vector)) as similarity,
          ce.entity_type
        FROM concept_embeddings ce
        JOIN concepts c ON ce.concept_id = c.id
        WHERE ce.entity_type = ANY($2::text[])
        AND (1 - (ce.embedding <=> $1::vector)) > $3
        ORDER BY ce.embedding <=> $1::vector
        LIMIT $4
        `,
        [
          JSON.stringify(queryEmbedding.embedding),
          entityTypes,
          minSimilarity,
          limit,
        ]
      );

      return results.rows.map((row) => ({
        conceptId: row.concept_id,
        title: row.title,
        description: row.description,
        difficulty: row.difficulty,
        similarity: parseFloat(row.similarity),
        entityType: row.entity_type,
      }));
    } catch (error: any) {
      throw new Error(`Search failed: ${error.message}`);
    }
  }

  /**
   * Batch generate embeddings for multiple concepts
   */
  async generateEmbeddingsForConcepts(
    conceptIds: string[]
  ): Promise<{ successful: number; failed: number; cost: number }> {
    let successful = 0;
    let failed = 0;
    let totalCost = 0;

    const batchId = this.generateBatchId();

    try {
      // Get concept data
      const concepts = await this.safeQuery(
        `
        SELECT id, title, description 
        FROM concepts 
        WHERE id = ANY($1::uuid[])
        `,
        [conceptIds]
      );

      // Log batch start
      await this.logBatchStart(batchId, concepts.rows.length);

      // Generate embeddings
      for (const concept of concepts.rows) {
        try {
          // Embed title and description
          const titleEmbedding = await this.generateEmbedding(concept.title);
          const descriptionEmbedding = await this.generateEmbedding(
            concept.description
          );
          const fullEmbedding = await this.generateEmbedding(
            `${concept.title} ${concept.description}`
          );

          // Store embeddings
          await this.storeEmbeddings([
            {
              conceptId: concept.id,
              contentType: "title",
              content: concept.title,
              ...titleEmbedding,
            },
            {
              conceptId: concept.id,
              contentType: "description",
              content: concept.description,
              ...descriptionEmbedding,
            },
            {
              conceptId: concept.id,
              contentType: "full",
              content: `${concept.title} ${concept.description}`,
              ...fullEmbedding,
            },
          ]);

          successful++;
          totalCost += (titleEmbedding.costEstimate || 0) +
            (descriptionEmbedding.costEstimate || 0) +
            (fullEmbedding.costEstimate || 0);
        } catch (error) {
          console.error(`Failed to embed concept ${concept.id}:`, error);
          failed++;
        }
      }

      // Log batch completion
      await this.logBatchCompletion(batchId, successful, failed, totalCost);

      return { successful, failed, cost: totalCost };
    } catch (error: any) {
      throw new Error(`Batch embedding failed: ${error.message}`);
    }
  }

  /**
   * Store embeddings in database
   */
  private async storeEmbeddings(
    embeddings: Array<{
      conceptId: string;
      contentType: string;
      content: string;
      embedding: number[];
      provider: "openai" | "local";
      modelUsed: string;
    }>
  ): Promise<void> {
    for (const emb of embeddings) {
      await this.safeQuery(
        `
        INSERT INTO concept_embeddings 
        (concept_id, entity_type, content_type, content, embedding, provider, model_used)
        VALUES ($1, $2, $3, $4, $5::vector, $6, $7)
        ON CONFLICT (concept_id, entity_type, content_type, provider) 
        DO UPDATE SET 
          embedding = $5::vector,
          content = $4,
          updated_at = CURRENT_TIMESTAMP
        `,
        [
          emb.conceptId,
          "concept",
          emb.contentType,
          emb.content,
          JSON.stringify(emb.embedding),
          emb.provider,
          emb.modelUsed,
        ]
      );
    }
  }

  /**
   * Log search query for analytics
   */
  private async logSearchQuery(
    userId: string,
    queryText: string,
    entityTypes: string[],
    limit: number
  ): Promise<void> {
    try {
      await this.safeQuery(
        `
        INSERT INTO vector_search_queries 
        (user_id, query_text, entity_types, limit_results)
        VALUES ($1, $2, $3, $4)
        `,
        [userId, queryText, entityTypes.join(","), limit]
      );
    } catch (error) {
      console.warn("Failed to log search query:", error);
    }
  }

  /**
   * Log batch embedding start
   */
  private async logBatchStart(batchId: string, conceptCount: number): Promise<void> {
    try {
      await this.safeQuery(
        `
        INSERT INTO embedding_metadata 
        (batch_id, concept_count, status)
        VALUES ($1, $2, 'processing')
        `,
        [batchId, conceptCount]
      );
    } catch (error) {
      console.warn("Failed to log batch start:", error);
    }
  }

  /**
   * Log batch embedding completion
   */
  private async logBatchCompletion(
    batchId: string,
    successful: number,
    failed: number,
    cost: number
  ): Promise<void> {
    try {
      await this.safeQuery(
        `
        UPDATE embedding_metadata
        SET 
          status = CASE WHEN $2 > 0 THEN 'completed' ELSE 'failed' END,
          concept_count = $3,
          total_cost_usd = $4,
          completed_at = CURRENT_TIMESTAMP
        WHERE batch_id = $1
        `,
        [batchId, failed, successful + failed, cost]
      );
    } catch (error) {
      console.warn("Failed to log batch completion:", error);
    }
  }

  /**
   * Generate unique batch ID
   */
  private generateBatchId(): string {
    return `batch-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}
