import { z } from "zod";

// Knowledge Node Type - Represents a single concept in the learning graph
export type KnowledgeNode = {
  id: string;
  label: string;
  confidence_score?: number;
  source_type?: string;
  source_url?: string;
  last_updated?: string;
  reliability_score?: number;
  created_at?: string;
  title?: string;
  description?: string;
  difficulty?: "beginner" | "intermediate" | "advanced";
  prerequisites: string[];
  learningResources?: LearningResource[];
  estimatedLearningTimeMinutes?: number;
  practiceProblems?: string[];
  skills?: string[];
  topics?: string[];
  updatedAt?: string;
  confidenceScore?: number;
  sourceMetadata?: {
    sourceType: string;
    sourceUrl: string;
    lastUpdated: string;
    reliabilityScore: number;
  };
};

// Learning Resource Type
export type LearningResource = {
  id: string;
  title: string;
  type: "video" | "article" | "tutorial" | "documentation" | "interactive";
  url: string;
  duration?: number; // in minutes
  difficulty: "beginner" | "intermediate" | "advanced";
};

// DAG Node for graph traversal
export type DAGNode = KnowledgeNode & {
  children: string[];
  parents: string[];
  topologicalOrder: number;
};

// Knowledge Graph Type
export type KnowledgeGraph = {
  nodes: Map<string, KnowledgeNode>;
  adjacencyList: Map<string, string[]>;
};

// User Path Type - represents user's progress through nodes
export type UserPathNode = {
  nodeId: string;
  status: "not-started" | "in-progress" | "completed" | "stuck";
  masteryScore: number;
  attemptCount: number;
  lastAttemptDate?: string;
  completedAt?: string;
  estimatedTimeRemaining?: number;
};

// Path Resolver Result
export type PathResolution = {
  recommendedOrder: string[]; // IDs in recommended learning order
  criticalPath: string[]; // Most important path to reach goal
  alternativePaths?: string[][];
  estimatedTotalTime: number; // in minutes
};

// Zod Schemas
export const LearningResourceSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  type: z.enum(["video", "article", "tutorial", "documentation", "interactive"]),
  url: z.string().url(),
  duration: z.number().optional(),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]),
});

export const KnowledgeNodeSchema = z.object({
  id: z.string(),
  label: z.string(),
  confidence_score: z.number().optional(),
  source_type: z.string().optional(),
  source_url: z.string().optional(),
  last_updated: z.string().optional(),
  reliability_score: z.number().optional(),
  created_at: z.string().optional(),
  title: z.string().optional(),
  description: z.string().optional(),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]).optional(),
  prerequisites: z.array(z.string()),
  learningResources: z.array(LearningResourceSchema).optional(),
  estimatedLearningTimeMinutes: z.number().positive().optional(),
  practiceProblems: z.array(z.string()).optional(),
  skills: z.array(z.string()).optional(),
  topics: z.array(z.string()).optional(),
  updatedAt: z.string().optional(),
  confidenceScore: z.number().optional(),
  sourceMetadata: z.object({
    sourceType: z.string(),
    sourceUrl: z.string(),
    lastUpdated: z.string(),
    reliabilityScore: z.number(),
  }).optional(),
});

export const DAGNodeSchema = KnowledgeNodeSchema.extend({
  children: z.array(z.string()),
  parents: z.array(z.string()),
  topologicalOrder: z.number(),
});

export const UserPathNodeSchema = z.object({
  nodeId: z.string(),
  status: z.enum(["not-started", "in-progress", "completed", "stuck"]),
  masteryScore: z.number().min(0).max(100),
  attemptCount: z.number().nonnegative(),
  lastAttemptDate: z.string().datetime().optional(),
  completedAt: z.string().datetime().optional(),
  estimatedTimeRemaining: z.number().optional(),
});

export const PathResolutionSchema = z.object({
  recommendedOrder: z.array(z.string()),
  criticalPath: z.array(z.string()),
  alternativePaths: z.array(z.array(z.string())).optional(),
  estimatedTotalTime: z.number().nonnegative(),
});
