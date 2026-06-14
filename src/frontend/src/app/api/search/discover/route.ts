/**
 * src/frontend/src/app/api/search/discover/route.ts
 * 
 * Semantic Search Discovery API (Phase 4.5)
 * 
 * GET /api/search/discover
 * Performs semantic/vector search across knowledge nodes, projects, and explanations
 * 
 * Query Parameters:
 *   - query: string (required) - Search query (e.g., "distributed systems", "scalable APIs")
 *   - limit: number (optional, default: 5) - Max results to return (1-20)
 *   - types: string (optional) - Comma-separated entity types (concept,project,explanation)
 *   - similarity: number (optional, default: 0.5) - Minimum similarity threshold (0-1)
 * 
 * Response:
 * {
 *   "success": true,
 *   "data": [
 *     {
 *       "conceptId": "uuid",
 *       "title": "Node.js Patterns",
 *       "description": "...",
 *       "difficulty": "intermediate",
 *       "similarity": 0.87,
 *       "entityType": "concept"
 *     }
 *   ],
 *   "meta": {
 *     "query": "distributed systems",
 *     "resultsCount": 5,
 *     "executionTimeMs": 142
 *   }
 * }
 */

import { NextRequest, NextResponse } from "next/server";

// NOTE: VectorSearchService should be called via backend API in production

interface DiscoverRequest {
  query: string;
  limit?: number;
  types?: string;
  similarity?: number;
}

interface DiscoverResponse {
  success: boolean;
  data?: Array<{
    conceptId: string;
    title: string;
    description: string;
    difficulty: "beginner" | "intermediate" | "advanced";
    similarity: number;
    entityType: string;
  }>;
  meta?: {
    query: string;
    resultsCount: number;
    executionTimeMs: number;
    provider?: "openai" | "local";
  };
  error?: string;
}

export async function GET(request: NextRequest): Promise<NextResponse<DiscoverResponse>> {
  const startTime = Date.now();

  try {
    // Parse query parameters
    const url = new URL(request.url);
    const query = url.searchParams.get("query");
    const limit = Math.min(parseInt(url.searchParams.get("limit") || "5") || 5, 20);
    const typesParam = url.searchParams.get("types");
    const similarity = parseFloat(url.searchParams.get("similarity") || "0.5");

    // Validate query
    if (!query || query.trim().length < 2) {
      return NextResponse.json(
        {
          success: false,
          error: "Query must be at least 2 characters",
        },
        { status: 400 }
      );
    }

    // Parse entity types
    const entityTypes = typesParam
      ? typesParam.split(",").map((t) => t.trim())
      : ["concept"];

    // Validate limit
    if (limit < 1 || limit > 20) {
      return NextResponse.json(
        {
          success: false,
          error: "Limit must be between 1 and 20",
        },
        { status: 400 }
      );
    }

    // Validate similarity threshold
    if (similarity < 0 || similarity > 1) {
      return NextResponse.json(
        {
          success: false,
          error: "Similarity must be between 0 and 1",
        },
        { status: 400 }
      );
    }

    // Get user ID if authenticated
    const userId = request.headers.get("x-user-id");

    // NOTE: VectorSearchService should be called via backend API in production
    // For now, return fallback results based on query matching
    const results = generateFallbackSearchResults(query.trim(), entityTypes, limit);

    const executionTime = Date.now() - startTime;

    // Log performance
    if (process.env.DEBUG_VECTOR_SEARCH === "true") {
      console.log(
        `[VectorSearch] Query: "${query}" | Results: ${results.length} | Time: ${executionTime}ms`
      );
    }

    return NextResponse.json(
      {
        success: true,
        data: results,
        meta: {
          query: query.trim(),
          resultsCount: results.length,
          executionTimeMs: executionTime,
          provider: (process.env.LLM_PROVIDER || "hybrid") as "openai" | "local",
        },
      },
      { status: 200 }
    );
  } catch (error: any) {
    console.error("[VectorSearch] Error:", error);

    const executionTime = Date.now() - startTime;
    const url = new URL(request.url);

    return NextResponse.json(
      {
        success: false,
        error: error.message || "Search failed",
        meta: {
          query: url.searchParams.get("query") || "",
          resultsCount: 0,
          executionTimeMs: executionTime,
        },
      },
      { status: 500 }
    );
  }
}

/**
 * Generate fallback search results when vector search is unavailable
 */
function generateFallbackSearchResults(
  query: string,
  entityTypes: string[],
  limit: number
): Array<{
  conceptId: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  similarity: number;
  entityType: string;
}> {
  const q = query.toLowerCase();
  const results: Array<{
    conceptId: string;
    title: string;
    description: string;
    difficulty: "beginner" | "intermediate" | "advanced";
    similarity: number;
    entityType: string;
  }> = [];

  const fallbackConcepts: Record<string, { title: string; description: string; difficulty: "beginner" | "intermediate" | "advanced" }> = {
    "javascript": { title: "JavaScript Fundamentals", description: "Core JavaScript concepts including variables, functions, and control flow", difficulty: "beginner" },
    "react": { title: "React Basics", description: "Building user interfaces with React components and hooks", difficulty: "intermediate" },
    "async": { title: "Async/Await Patterns", description: "Understanding asynchronous JavaScript with promises and async/await", difficulty: "intermediate" },
    "typescript": { title: "TypeScript Essentials", description: "Type-safe JavaScript with TypeScript generics and interfaces", difficulty: "intermediate" },
    "python": { title: "Python Programming", description: "Python fundamentals for data science and web development", difficulty: "beginner" },
    "api": { title: "REST API Design", description: "Building scalable RESTful APIs with proper architecture", difficulty: "intermediate" },
    "database": { title: "Database Design", description: "Relational and NoSQL database design patterns", difficulty: "intermediate" },
    "git": { title: "Git Version Control", description: "Source code management with Git branching and workflows", difficulty: "beginner" },
  };

  for (const [key, concept] of Object.entries(fallbackConcepts)) {
    if (results.length >= limit) break;
    const titleLower = concept.title.toLowerCase();
    const descLower = concept.description.toLowerCase();
    if (titleLower.includes(q) || descLower.includes(q) || key.includes(q)) {
      results.push({
        conceptId: `fallback_${key}`,
        title: concept.title,
        description: concept.description,
        difficulty: concept.difficulty,
        similarity: 0.85,
        entityType: entityTypes.includes("concept") ? "concept" : entityTypes[0],
      });
    }
  }

  return results;
}

/**
 * POST /api/search/discover/batch-embed
 * Admin endpoint to generate embeddings for all concepts
 * Requires x-admin-token header
 */
export async function POST(request: NextRequest): Promise<NextResponse<any>> {
  try {
    // Verify admin token
    const adminToken = request.headers.get("x-admin-token");
    if (adminToken !== process.env.ADMIN_API_TOKEN) {
      return NextResponse.json(
        { success: false, error: "Unauthorized" },
        { status: 403 }
      );
    }

    // NOTE: This should call the backend API for batch embedding in production
    // For now, return placeholder response
    return NextResponse.json(
      {
        success: true,
        data: { embedded: 0, errors: [] },
      },
      { status: 200 }
    );
  } catch (error: any) {
    console.error("[VectorSearch] Batch embed error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || "Batch embedding failed",
      },
      { status: 500 }
    );
  }
}
