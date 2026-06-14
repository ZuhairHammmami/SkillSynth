/**
 * src/frontend/src/app/api/mastery/user-path/route.ts
 * 
 * Identity Handshake API
 * Maps Supabase auth.uid() to user_mastery table
 * 
 * GET /api/mastery/user-path
 * Returns the user's current mastery state and accessible starting nodes
 */

import { NextRequest, NextResponse } from "next/server";

interface MasteryRecord {
  id: string;
  user_id: string;
  current_node_id: string | null;
  path_history: string[];
  allowed_paths: string[];
  custom_skill_overrides: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface UserMasteryResponse {
  success: boolean;
  data?: {
    userId: string;
    currentNodeId: string | null;
    pathHistory: string[];
    allowedPaths: string[];
    customSkillOverrides: Record<string, any>;
    isNewUser: boolean;
    createdAt: string;
    updatedAt: string;
  };
  error?: string;
  startingNodes?: string[]; // Root nodes user can access
}

/**
 * GET /api/mastery/user-path
 * Fetch or initialize user's mastery record
 */
export async function GET(request: NextRequest): Promise<NextResponse<UserMasteryResponse>> {
  try {
    // Get auth user ID from request headers (set by middleware)
    const userId = request.headers.get("x-user-id");

    if (!userId) {
      return NextResponse.json(
        {
          success: false,
          error: "Unauthorized: No authenticated user found",
        },
        { status: 401 }
      );
    }

    // Query Supabase for existing user_mastery record
    const masteryRecord = await queryUserMastery(userId);

    if (masteryRecord) {
      // User exists - return their current state
      return NextResponse.json(
        {
          success: true,
          data: {
            userId,
            currentNodeId: masteryRecord.current_node_id,
            pathHistory: masteryRecord.path_history || [],
            allowedPaths: masteryRecord.allowed_paths || [],
            customSkillOverrides: masteryRecord.custom_skill_overrides || {},
            isNewUser: false,
            createdAt: masteryRecord.created_at,
            updatedAt: masteryRecord.updated_at,
          },
        },
        { status: 200 }
      );
    }

    // New user - initialize mastery record
    const newRecord = await initializeUserMastery(userId);

    if (!newRecord) {
      return NextResponse.json(
        {
          success: false,
          error: "Failed to initialize user mastery record",
        },
        { status: 500 }
      );
    }

    return NextResponse.json(
      {
        success: true,
        data: {
          userId,
          currentNodeId: null,
          pathHistory: [],
          allowedPaths: [], // Will be populated by PathResolver
          customSkillOverrides: {},
          isNewUser: true,
          createdAt: newRecord.created_at,
          updatedAt: newRecord.updated_at,
        },
      },
      { status: 201 }
    );
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error occurred";

    console.error("[Identity Handshake Error]", errorMessage);

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
 * Query user's existing mastery record from Supabase
 */
async function queryUserMastery(userId: string): Promise<MasteryRecord | null> {
  try {
    // TODO: Replace with actual Supabase query
    // This would be: const { data, error } = await supabase
    //   .from('user_mastery')
    //   .select('*')
    //   .eq('user_id', userId)
    //   .single();

    // For now, returning null (user not found) to trigger initialization
    return null;
  } catch (error) {
    console.error("[DB Query Error]", error);
    return null;
  }
}

/**
 * Initialize a new user_mastery record
 * This is called for new users on their first login
 */
async function initializeUserMastery(userId: string): Promise<MasteryRecord | null> {
  try {
    const now = new Date().toISOString();

    // TODO: Replace with actual Supabase insert
    // This would be: const { data, error } = await supabase
    //   .from('user_mastery')
    //   .insert({
    //     user_id: userId,
    //     current_node_id: null,
    //     path_history: [],
    //     allowed_paths: [],
    //     custom_skill_overrides: {},
    //     created_at: now,
    //     updated_at: now,
    //   })
    //   .select()
    //   .single();

    // Mock response for now
    return {
      id: `mastery-${userId}`,
      user_id: userId,
      current_node_id: null,
      path_history: [],
      allowed_paths: [],
      custom_skill_overrides: {},
      created_at: now,
      updated_at: now,
    };
  } catch (error) {
    console.error("[DB Insert Error]", error);
    return null;
  }
}
