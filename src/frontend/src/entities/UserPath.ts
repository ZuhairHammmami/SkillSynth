import { z } from "zod";

// User Path Type - represents the user's learning journey
export type UserPath = {
  id: string;
  user_id: string;
  userId?: string;
  title: string;
  pathName: string;
  description?: string;
  nodes: UserPathNode[];
  current_node_id?: string;
  currentNode?: string;
  progress: number;
  completed_at?: string;
  completedAssessments?: string[];
  created_at: string;
  createdAt?: string;
  updated_at: string;
  updatedAt?: string;
  pathHistory: string[];
  goalConceptId?: string;
  customSkillOverrides?: Record<string, { skipped?: boolean; masteryLevel?: number }>;
  skillOverrides?: Record<string, { skipped?: boolean; masteryLevel?: number }>;
  allowedPaths?: string[];
};

export type UserPathInput = {
  id?: string;
  user_id?: string;
  userId?: string;
  title?: string;
  pathName?: string;
  description?: string;
  nodes?: UserPathNode[];
  current_node_id?: string;
  currentNode?: string;
  progress?: number;
  completed_at?: string;
  completedAssessments?: string[];
  created_at?: string;
  createdAt?: string;
  updated_at?: string;
  updatedAt?: string;
  pathHistory?: string[];
  goalConceptId?: string;
  customSkillOverrides?: Record<string, { skipped?: boolean; masteryLevel?: number }>;
  skillOverrides?: Record<string, { skipped?: boolean; masteryLevel?: number }>;
  allowedPaths?: string[];
};

export type UserPathNode = {
  nodeId: string;
  status: "not-started" | "in-progress" | "completed" | "stuck";
  masteryScore: number;
  attemptCount: number;
  lastAttemptDate?: string;
  completedAt?: string;
  estimatedTimeRemaining?: number;
};

// Path Progress Type
export type PathProgress = {
  totalNodes: number;
  completedNodes: number;
  inProgressNodes: number;
  stuckNodes: number;
  progressPercentage: number;
  estimatedTimeRemaining: number;
  averageMasteryScore: number;
};

// Path Milestone Type
export type PathMilestone = {
  id: string;
  userPathId: string;
  nodeId: string;
  milestoneType: "concept-mastered" | "assessment-passed" | "series-completed";
  achievedAt: string;
  reward?: string;
};

// Zod Schemas
export const UserPathNodeSchema = z.object({
  nodeId: z.string(),
  status: z.enum(["not-started", "in-progress", "completed", "stuck"]),
  masteryScore: z.number().min(0).max(100),
  attemptCount: z.number().nonnegative(),
  lastAttemptDate: z.string().datetime().optional(),
  completedAt: z.string().datetime().optional(),
  estimatedTimeRemaining: z.number().optional(),
});

export const UserPathSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  nodes: z.array(UserPathNodeSchema),
  current_node_id: z.string().optional(),
  currentNode: z.string().optional(),
  progress: z.number().min(0).max(100),
  completed_at: z.string().datetime().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  pathHistory: z.array(z.string()),
  goalConceptId: z.string().optional(),
  customSkillOverrides: z.record(z.string(), z.object({
    skipped: z.boolean().optional(),
    masteryLevel: z.number().optional(),
  })).optional(),
  skillOverrides: z.record(z.string(), z.object({
    skipped: z.boolean().optional(),
    masteryLevel: z.number().optional(),
  })).optional(),
  allowedPaths: z.array(z.string()).optional(),
});

export const PathProgressSchema = z.object({
  totalNodes: z.number().nonnegative(),
  completedNodes: z.number().nonnegative(),
  inProgressNodes: z.number().nonnegative(),
  stuckNodes: z.number().nonnegative(),
  progressPercentage: z.number().min(0).max(100),
  estimatedTimeRemaining: z.number().nonnegative(),
  averageMasteryScore: z.number().min(0).max(100),
});

export const PathMilestoneSchema = z.object({
  id: z.string().uuid(),
  userPathId: z.string().uuid(),
  nodeId: z.string(),
  milestoneType: z.enum(["concept-mastered", "assessment-passed", "series-completed"]),
  achievedAt: z.string().datetime(),
  reward: z.string().optional(),
});
