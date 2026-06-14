/**
 * src/frontend/src/app/api/projects/submit/route.ts
 * 
 * Project Submission API
 * POST /api/projects/submit
 * 
 * Handles project milestone submissions for knowledge node mastery validation
 * Supports multiple submission types: GitHub URL, file upload, code snippet, demo link
 */

import { NextRequest, NextResponse } from "next/server";
// Services located outside frontend - would call backend API in production
// import { ProjectSubmissionSchema } from "../../../../entities/EngineeringProject";
// import { ProjectSubmissionService } from "../../../../services/ProjectSubmissionService";

interface SubmitProjectRequest {
  userId: string;
  projectId: string;
  nodeId: string;
  milestone: string; // design, implementation, testing, deployment, documentation
  submissionType: "file_upload" | "github_url" | "code_snippet" | "demo_link";
  submissionData: {
    fileUrl?: string;
    githubUrl?: string;
    codeSnippet?: string;
    demoLink?: string;
  };
  description?: string;
}

interface SubmitProjectResponse {
  success: boolean;
  data?: {
    submissionId: string;
    message: string;
    warnings?: string[];
  };
  error?: string;
  errors?: string[];
}

/**
 * POST /api/projects/submit
 * Submit project work for a milestone
 */
export async function POST(
  request: NextRequest
): Promise<NextResponse<SubmitProjectResponse>> {
  try {
    const body: SubmitProjectRequest = await request.json();

    // Verify authentication
    const userId = request.headers.get("x-user-id");
    if (!userId || userId !== body.userId) {
      return NextResponse.json(
        {
          success: false,
          error: "Unauthorized: User ID mismatch or missing authentication",
        },
        { status: 403 }
      );
    }

    // Validate required fields
    const requiredFields = ["userId", "projectId", "nodeId", "milestone", "submissionType"];
    const missingFields = requiredFields.filter(field => !body[field as keyof SubmitProjectRequest]);

    if (missingFields.length > 0) {
      return NextResponse.json(
        {
          success: false,
          error: `Missing required fields: ${missingFields.join(", ")}`,
        },
        { status: 400 }
      );
    }

    // Submit and validate project work
    // Would call backend API: const result = await ProjectSubmissionService.submitProjectWork({...});
    const result = {
      isValid: true,
      errors: [],
      warnings: [],
      submissionId: "pending-" + Date.now()
    };

    if (!result.isValid) {
      return NextResponse.json(
        {
          success: false,
          errors: result.errors,
        },
        { status: 422 }
      );
    }

    return NextResponse.json(
      {
        success: true,
        data: {
          submissionId: result.submissionId!,
          message: `Project submission received for milestone: ${body.milestone}`,
          warnings: result.warnings.length > 0 ? result.warnings : undefined,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("[Project Submission Error]", error);

    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/projects/submit
 * Check milestone completion status for a user
 */
export async function GET(
  request: NextRequest
): Promise<NextResponse<{ success: boolean; completed?: boolean; error?: string }>> {
  try {
    const userId = request.headers.get("x-user-id");
    if (!userId) {
      return NextResponse.json(
        {
          success: false,
          error: "Unauthorized: Missing user authentication",
        },
        { status: 403 }
      );
    }

    const searchParams = request.nextUrl.searchParams;
    const projectId = searchParams.get("projectId");
    const nodeId = searchParams.get("nodeId");
    const milestone = searchParams.get("milestone");

    if (!projectId || !nodeId || !milestone) {
      return NextResponse.json(
        {
          success: false,
          error: "Missing required query parameters: projectId, nodeId, milestone",
        },
        { status: 400 }
      );
    }

    // Would call backend API: const completed = await ProjectSubmissionService.checkMilestoneCompletion(...);
    const completed = false;

    return NextResponse.json(
      {
        success: true,
        completed,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("[Milestone Check Error]", error);

    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 }
    );
  }
}
