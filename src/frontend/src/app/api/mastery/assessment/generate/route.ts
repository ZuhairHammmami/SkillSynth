/**
 * src/frontend/src/app/api/mastery/assessment/generate/route.ts
 * 
 * Assessment Generation API
 * Generates dynamic quizzes for skill validation before mastery is granted
 * 
 * GET /api/mastery/assessment/generate?conceptId=<uuid>&userId=<uuid>&difficulty=intermediate
 * Returns a dynamically generated assessment
 */

import { NextRequest, NextResponse } from "next/server";
import { AssessmentService } from "@/shared/services/AssessmentService";
import { CreateAssessmentRequestSchema } from "@/entities/Assessment";

interface GenerateAssessmentResponse {
  success: boolean;
  data?: {
    assessment: any;
    totalTimeEstimate: number;
    passingScore: number;
  };
  error?: string;
  meta?: { provider: string };
}

function generateFallbackAssessment(conceptId: string, difficulty: string) {
  const questionCount = difficulty === "beginner" ? 5 : difficulty === "intermediate" ? 7 : 10;
  const questions = [];
  for (let i = 0; i < questionCount; i++) {
    questions.push({
      id: `fallback_${i}`,
      conceptId,
      questionText: `What is the primary purpose of ${conceptId}?`,
      questionType: "multiple-choice",
      difficulty,
      options: [
        "A) To solve a specific category of problems",
        "B) To make code run faster",
        "C) To replace all other approaches",
        "D) It has no real purpose",
      ],
      estimatedTimeSeconds: 30,
    });
  }
  return {
    id: `assessment_${Date.now()}`,
    conceptId,
    title: `Assessment: ${conceptId}`,
    description: `Validate your understanding of ${conceptId}`,
    questions,
    totalTimeEstimateSeconds: questions.length * 30,
    passingScore: 80,
    difficulty,
    createdAt: new Date().toISOString(),
    expiresAt: new Date(Date.now() + 86400000).toISOString(),
  };
}

/**
 * GET /api/mastery/assessment/generate
 * Generate a dynamic assessment for a specific concept
 * 
 * Query Parameters:
 * - conceptId: UUID of the concept to assess
 * - userId: UUID of the user (from auth header)
 * - difficulty: Optional - 'beginner', 'intermediate', 'advanced'
 * - previousAttempts: Optional - number of times user has attempted
 */
export async function GET(
  request: NextRequest
): Promise<NextResponse<GenerateAssessmentResponse>> {
  try {
    const searchParams = request.nextUrl.searchParams;
    const conceptId = searchParams.get("conceptId");
    const userId = searchParams.get("userId") || request.headers.get("x-user-id");
    const difficulty = (searchParams.get("difficulty") ||
      "intermediate") as any;
    const previousAttempts = parseInt(searchParams.get("previousAttempts") || "0", 10);

    // Validate required parameters
    if (!conceptId) {
      return NextResponse.json(
        {
          success: false,
          error: "Missing required parameter: conceptId",
        },
        { status: 400 }
      );
    }

    if (!userId) {
      return NextResponse.json(
        {
          success: false,
          error: "Unauthorized: User ID not found in request",
        },
        { status: 401 }
      );
    }

    // Verify user authorization
    const authenticatedUserId = request.headers.get("x-user-id");
    if (authenticatedUserId && authenticatedUserId !== userId) {
      return NextResponse.json(
        {
          success: false,
          error: "Unauthorized: User ID mismatch",
        },
        { status: 403 }
      );
    }

    // Generate assessment
    const assessment = await AssessmentService.generateAssessment({
      conceptId,
      userId,
      difficulty,
      previousAttempts,
    });

    // Remove correct answers before sending to client (to prevent cheating)
    const cleanedAssessment = {
      ...assessment,
      questions: assessment.questions.map((q) => ({
        id: q.id,
        conceptId: q.conceptId,
        questionText: q.questionText,
        questionType: q.questionType,
        difficulty: q.difficulty,
        options: q.options,
        estimatedTimeSeconds: q.estimatedTimeSeconds,
        // NOTE: correctAnswer, explanation are NOT sent to client
      })),
    };

    console.log(
      `[Assessment Generated] User: ${userId}, Concept: ${conceptId}, Difficulty: ${difficulty}`
    );

    return NextResponse.json(
      {
        success: true,
        data: {
          assessment: cleanedAssessment,
          totalTimeEstimate: assessment.totalTimeEstimateSeconds,
          passingScore: assessment.passingScore,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";

    console.error("[Assessment Generation Error]", errorMessage);

    const url = new URL(request.url);
    const conceptId = url.searchParams.get("conceptId") || "unknown";
    const difficulty = url.searchParams.get("difficulty") || "intermediate";
    const fallback = generateFallbackAssessment(conceptId, difficulty);

    return NextResponse.json(
      {
        success: true,
        data: {
          assessment: fallback,
          totalTimeEstimate: fallback.questions.length * 30,
          passingScore: 80,
        },
        meta: { provider: "fallback" },
      },
      { status: 200 }
    );
  }
}
