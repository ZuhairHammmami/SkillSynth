/**
 * src/frontend/src/app/api/mastery/progress/route.ts
 * 
 * Mastery Progression API
 * Handles updates to user_mastery when concepts are completed
 * 
 * POST /api/mastery/progress
 * Updates path history and current node
 */

import { NextRequest, NextResponse } from "next/server";

interface ProgressUpdateRequest {
  userId: string;
  completedNodeId: string;
  pathHistory: string[];
  timestamp: string;
}

interface ProgressUpdateResponse {
  success: boolean;
  data?: {
    userId: string;
    completedNodeId: string;
    updatedAt: string;
  };
  error?: string;
}

/**
 * POST /api/mastery/progress
 * Update user mastery when they complete a node
 */
export async function POST(
  request: NextRequest
): Promise<NextResponse<ProgressUpdateResponse>> {
  try {
    const body: ProgressUpdateRequest = await request.json();

    // Validate required fields
    if (!body.userId || !body.completedNodeId || !body.pathHistory) {
      return NextResponse.json(
        {
          success: false,
          error: "Missing required fields: userId, completedNodeId, pathHistory",
        },
        { status: 400 }
      );
    }

    // Verify user authorization (ensure x-user-id matches userId)
    const authenticatedUserId = request.headers.get("x-user-id");
    if (authenticatedUserId && authenticatedUserId !== body.userId) {
      return NextResponse.json(
        {
          success: false,
          error: "Unauthorized: User ID mismatch",
        },
        { status: 403 }
      );
    }

    // Update user_mastery table
    const updateResult = await updateUserMastery(
      body.userId,
      body.completedNodeId,
      body.pathHistory
    );

    if (!updateResult.success) {
      return NextResponse.json(
        {
          success: false,
          error: updateResult.error,
        },
        { status: 500 }
      );
    }

    return NextResponse.json(
      {
        success: true,
        data: {
          userId: body.userId,
          completedNodeId: body.completedNodeId,
          updatedAt: new Date().toISOString(),
        },
      },
      { status: 200 }
    );
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";

    console.error("[Mastery Progress Error]", errorMessage);

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
 * Update user_mastery record in the database
 */
async function updateUserMastery(
  userId: string,
  completedNodeId: string,
  pathHistory: string[]
): Promise<{ success: boolean; error?: string }> {
  try {
    // TODO: Replace with actual Supabase update
    // This would be:
    // const { error } = await supabase
    //   .from('user_mastery')
    //   .update({
    //     current_node_id: completedNodeId,
    //     path_history: pathHistory,
    //     updated_at: new Date().toISOString(),
    //   })
    //   .eq('user_id', userId);
    //
    // if (error) {
    //   return { success: false, error: error.message };
    // }

    console.log(
      `[Mastery Updated] User: ${userId}, Completed: ${completedNodeId}, Path: ${pathHistory.length}`
    );

    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Database update failed",
    };
  }
}
