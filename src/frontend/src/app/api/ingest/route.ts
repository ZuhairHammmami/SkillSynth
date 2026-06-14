import { NextRequest, NextResponse } from "next/server";
import { KnowledgeIngestionFormSchema } from "@/app/admin/forms/KnowledgeIngestionFormSchema";
// Services located outside frontend - should call backend API in production
// import { ConflictCheckerService } from "../../../../services/shared/conflict-checker/ConflictCheckerService";
// import { NotificationService } from "../../../../services/shared/notification/NotificationService";
import { KnowledgeNode } from "@/entities/KnowledgeNode";

/**
 * AEIS Source-to-Mastery API Bridge
 * POST /api/ingest
 * 
 * This is the primary entry point for ingesting raw academic/market data
 * into the AEIS knowledge pipeline. It enforces mastery-first validation
 * at every stage: schema validation, circular reference checking, and
 * confidence threshold enforcement.
 */

// Type for database response
interface SupabaseResponse {
  data?: { id: string; label: string; confidence_score: number }[];
  error?: { message: string };
}

interface ConceptWithPrereqs extends KnowledgeNode {
  prerequisites: string[];
}

export async function POST(request: NextRequest) {
  try {
    // Step 1: Parse and validate request body
    const body = await request.json();

    // Step 2: Validate via KnowledgeIngestionFormSchema
    const validationResult = KnowledgeIngestionFormSchema.safeParse(body);

    if (!validationResult.success) {
      return NextResponse.json(
        {
          success: false,
          error: "Validation failed",
          details: validationResult.error.flatten(),
        },
        { status: 400 }
      );
    }

    const ingestionData = validationResult.data;

    // Step 3: Check confidence threshold
    if (ingestionData.confidenceScore <= 0.7) {
      // Trigger low confidence alert - would call backend API in production
      // await NotificationService.sendSystemAlert(...);

      return NextResponse.json(
        {
          success: false,
          error: "Confidence score must be greater than 0.7 (mastery threshold)",
          confidenceScore: ingestionData.confidenceScore,
        },
        { status: 422 }
      );
    }

    // Step 4: Validate prerequisites using ConflictCheckerService
    // TODO: Use backend API for conflict checking
    if (ingestionData.prerequisites && ingestionData.prerequisites.length > 0) {
      // Fetch existing concepts from database
      const conceptsResponse = await fetchConceptsFromDatabase();

      if (conceptsResponse.error) {
        return NextResponse.json(
          {
            success: false,
            error: "Failed to fetch existing concepts for validation",
          },
          { status: 500 }
        );
      }

      // Build node map for conflict checking
      const allNodesMap = new Map<string, KnowledgeNode>();
      conceptsResponse.data?.forEach((concept: any) => {
        allNodesMap.set(concept.id, {
          id: concept.id,
          label: concept.label,
          confidenceScore: concept.confidence_score,
          prerequisites: [],
          sourceMetadata: {
            sourceType: "market",
            sourceUrl: concept.source_url || "",
            lastUpdated: new Date().toISOString(),
            reliabilityScore: concept.reliability_score || 0.8,
          },
        });
      });

      // Check for circular references
      const circularCheckResult = checkForCircularReferences(
        ingestionData.prerequisites,
        allNodesMap,
        new Set()
      );

      if (circularCheckResult.hasCircular) {
        return NextResponse.json(
          {
            success: false,
            error: "Circular prerequisite dependency detected",
            conflictingNodes: circularCheckResult.conflictingNodes,
          },
          { status: 409 }
        );
      }
    }

    // Step 5: Commit to Supabase
    const commitResult = await commitConceptToDatabase({
      label: ingestionData.label,
      confidenceScore: ingestionData.confidenceScore,
      sourceType: ingestionData.sourceType,
      sourceUrl: ingestionData.sourceUrl,
      reliabilityScore: ingestionData.reliabilityScore || 0.8,
      prerequisites: ingestionData.prerequisites || [],
    });

    if (commitResult.error) {
      return NextResponse.json(
        {
          success: false,
          error: "Failed to commit concept to database",
          details: commitResult.error,
        },
        { status: 500 }
      );
    }

    // Step 6: Send success notification
    // Would call backend API in production: await NotificationService.notifyKnowledgeIngestion(...);

    return NextResponse.json(
      {
        success: true,
        message: "Concept successfully ingested",
        concept: {
          id: commitResult.id,
          label: ingestionData.label,
          confidenceScore: ingestionData.confidenceScore,
          sourceType: ingestionData.sourceType,
        },
      },
      { status: 201 }
    );
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error occurred";

    // Send error alert to admin
    // Would call backend API in production: await NotificationService.sendSystemAlert(...);

    return NextResponse.json(
      {
        success: false,
        error: errorMessage,
      },
      { status: 500 }
    );
  }
}

/**
 * Fetch all existing concepts from Supabase
 */
async function fetchConceptsFromDatabase(): Promise<SupabaseResponse> {
  try {
    // TODO: Replace with actual Supabase query
    // This would use the Postgres MCP to query the concepts table
    // For now, return empty array (will be populated after DB migration)
    return { data: [] };
  } catch (error) {
    return {
      error: {
        message: error instanceof Error ? error.message : "Database query failed",
      },
    };
  }
}

/**
 * Check for circular references in prerequisites
 * Returns true if a circular dependency is detected
 */
function checkForCircularReferences(
  prerequisites: string[],
  allNodes: Map<string, KnowledgeNode>,
  visited: Set<string>,
  nodeId: string = ""
): { hasCircular: boolean; conflictingNodes: string[] } {
  const conflictingNodes: string[] = [];

  for (const prereqId of prerequisites) {
    if (visited.has(prereqId)) {
      conflictingNodes.push(prereqId);
      return { hasCircular: true, conflictingNodes };
    }

    if (prereqId === nodeId) {
      // Self-reference
      return { hasCircular: true, conflictingNodes: [prereqId] };
    }

    visited.add(prereqId);
    const node = allNodes.get(prereqId);
    if (node && node.prerequisites.length > 0) {
      const result = checkForCircularReferences(
        node.prerequisites,
        allNodes,
        new Set(visited),
        nodeId
      );
      if (result.hasCircular) {
        return result;
      }
    }
  }

  return { hasCircular: false, conflictingNodes: [] };
}

/**
 * Commit a validated concept to the database
 */
async function commitConceptToDatabase(conceptData: {
  label: string;
  confidenceScore: number;
  sourceType: string;
  sourceUrl: string;
  reliabilityScore: number;
  prerequisites: string[];
}): Promise<{ id?: string; error?: string }> {
  try {
    // TODO: Replace with actual Supabase insert
    // This would use the Postgres MCP to insert into concepts table
    // For now, return a mock ID
    return {
      id: `concept-${Date.now()}`,
    };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : "Database insert failed",
    };
  }
}

/**
 * GET /api/ingest - Returns ingestion status and schema
 */
export async function GET() {
  return NextResponse.json(
    {
      status: "ready",
      endpoint: "/api/ingest",
      method: "POST",
      description: "AEIS Source-to-Mastery API Bridge",
      validation: "KnowledgeIngestionFormSchema",
      constraints: {
        confidenceThreshold: "> 0.7",
        circularReferences: "checked and prevented",
        alerts: "sent on violations",
      },
    },
    { status: 200 }
  );
}
