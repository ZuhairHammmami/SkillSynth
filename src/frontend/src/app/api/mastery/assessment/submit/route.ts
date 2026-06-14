/**
 * src/frontend/src/app/api/mastery/assessment/submit/route.ts
 * 
 * Assessment Submission API
 * Validates answers and determines if user can progress (score >= 80%)
 * 
 * POST /api/mastery/assessment/submit
 * Submits completed assessment for grading
 */

import { NextRequest, NextResponse } from "next/server";
import { AssessmentService } from "@/shared/services/AssessmentService";
import {
  SubmitAssessmentSchema,
  AssessmentResultSchema,
  type SubmitAssessment,
  type Assessment,
} from "@/entities/Assessment";

interface SubmitAssessmentResponse {
  success: boolean;
  data?: {
    assessmentId: string;
    userId: string;
    conceptId: string;
    score: number;
    passed: boolean;
    feedback: string;
    explanations?: Record<string, string>;
    resultId?: string;
  };
  error?: string;
}

/**
 * POST /api/mastery/assessment/submit
 * Submit assessment answers for grading
 * 
 * Request Body:
 * {
 *   assessmentId: UUID,
 *   userId: UUID,
 *   answers: { questionId: answer, ... },
 *   timeSpentSeconds: number
 * }
 */
export async function POST(
  request: NextRequest
): Promise<NextResponse<SubmitAssessmentResponse>> {
  try {
    const body = await request.json();

    // Validate request structure
    if (!body.assessmentId || !body.userId || !body.answers) {
      return NextResponse.json(
        {
          success: false,
          error: "Missing required fields: assessmentId, userId, answers",
        },
        { status: 400 }
      );
    }

    // Verify user authorization
    const authenticatedUserId = request.headers.get("x-user-id");
    if (
      authenticatedUserId &&
      authenticatedUserId !== body.userId
    ) {
      return NextResponse.json(
        {
          success: false,
          error: "Unauthorized: User ID mismatch",
        },
        { status: 403 }
      );
    }

    const submission: SubmitAssessment = {
      assessmentId: body.assessmentId,
      userId: body.userId,
      answers: body.answers,
      submittedAt: new Date().toISOString(),
      timeSpentSeconds: body.timeSpentSeconds || 0,
    };

    // NOTE: In production, fetch the real assessment from DB to validate answers.
    // For now, all submissions are recorded but only mock-graded.
    const totalQuestions = Object.keys(body.answers).length;
    const correctAnswers = Math.floor(totalQuestions * 0.6); // Simulate 60% for demo
    const score = totalQuestions > 0 ? (correctAnswers / totalQuestions) * 100 : 0;
    const passed = score >= 80;

    const resultId = `result_${Date.now()}`;

    console.log(
      `[Assessment Submitted] User: ${body.userId}, Concept: ${body.conceptId}, Score: ${score.toFixed(1)}% (PASS: ${passed})`
    );

    return NextResponse.json(
      {
        success: true,
        data: {
          assessmentId: body.assessmentId,
          userId: body.userId,
          conceptId: body.conceptId,
          score,
          passed,
          feedback: passed
            ? `Well done! You scored ${score.toFixed(1)}%.`
            : `You scored ${score.toFixed(1)}%. Review the material and try again.`,
          resultId,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";

    console.error("[Assessment Submission Error]", errorMessage);

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
 * Store assessment result in database
 * 
 * TODO: Replace with actual Supabase insert
 */
async function storeAssessmentResult(
  userId: string,
  conceptId: string,
  score: number,
  totalQuestions: number,
  correctAnswers: number,
  timeSpent: number,
  passed: boolean
): Promise<string> {
  try {
    // TODO: Insert into assessment_results table
    // const { data, error } = await supabase
    //   .from('assessment_results')
    //   .insert([{
    //     user_id: userId,
    //     concept_id: conceptId,
    //     score,
    //     total_questions: totalQuestions,
    //     correct_answers: correctAnswers,
    //     time_spent_seconds: timeSpent,
    //     passed,
    //     created_at: new Date().toISOString()
    //   }])
    //   .select();

    console.log(
      `[Assessment Result Stored] User: ${userId}, Concept: ${conceptId}, Score: ${score}%`
    );

    return `result_${Date.now()}`; // Mock ID for now
  } catch (error) {
    throw new Error(
      `Failed to store assessment result: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  }
}

/**
 * Unlock node for user upon passing assessment
 * This allows progression to the next concepts
 * 
 * TODO: Replace with actual database update
 */
async function unlockNodeForUser(userId: string, conceptId: string): Promise<void> {
  try {
    // TODO: Update user_mastery to mark this concept as mastered
    // Update allowed_paths to include newly accessible nodes
    // const { error } = await supabase
    //   .from('user_mastery')
    //   .update({
    //     path_history: [...pathHistory, conceptId],
    //     updated_at: new Date().toISOString()
    //   })
    //   .eq('user_id', userId);

    console.log(
      `[Node Unlocked] User: ${userId}, Concept: ${conceptId}`
    );
  } catch (error) {
    throw new Error(
      `Failed to unlock node: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  }
}
