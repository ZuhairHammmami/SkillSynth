import { z } from "zod";

/**
 * Engineering Project Phase enum
 * Defines the maturity level of an engineering project
 */
export const EngineeringPhaseEnum = z.enum(["MVP", "Production", "Scalable"]);

/**
 * Project Submission Type
 * Determines how project milestone evidence is submitted
 */
export const ProjectSubmissionTypeEnum = z.enum(["file_upload", "github_url", "code_snippet", "demo_link"]);

/**
 * Project Milestone enum
 * Defines validation gates for mastery progression
 */
export const ProjectMilestoneEnum = z.enum(["design", "implementation", "testing", "deployment", "documentation"]);

/**
 * Enhanced Engineering Project Schema (Phase 4.0)
 * Now supports project-based validation gates for mastery progression
 */
export const EngineeringProjectSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(3),
  description: z.string().optional(),
  phase: EngineeringPhaseEnum,
  startDate: z.string().datetime().optional(),
  endDate: z.string().datetime().optional(),
  knowledgeNodes: z.array(z.string().uuid()),
  // Phase 4.0 additions
  requiredMilestones: z.array(ProjectMilestoneEnum).default([]),
  estimatedHours: z.number().positive().optional(),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]).default("intermediate"),
  repositoryUrl: z.string().url().optional(),
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type EngineeringProject = z.infer<typeof EngineeringProjectSchema>;

/**
 * Project Node Requirement (Bridge Table)
 * Links specific knowledge nodes to required project milestones
 * 
 * Example: A user must complete the "implementation" milestone of project X
 * before mastering the "async-programming" concept node
 */
export const ProjectNodeRequirementSchema = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid(),
  nodeId: z.string().uuid(), // Knowledge node ID
  requiredMilestone: ProjectMilestoneEnum,
  passingCriteria: z.string().optional().describe("Acceptance criteria for this milestone"),
  createdAt: z.string().datetime(),
});

export type ProjectNodeRequirement = z.infer<typeof ProjectNodeRequirementSchema>;

/**
 * Project Submission Schema
 * Tracks user submissions for project milestones
 */
export const ProjectSubmissionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  projectId: z.string().uuid(),
  nodeId: z.string().uuid(), // Which knowledge node is being validated
  milestone: ProjectMilestoneEnum,
  submissionType: ProjectSubmissionTypeEnum,
  // Submission data - one of these will be populated
  fileUrl: z.string().url().optional(),
  githubUrl: z.string().url().optional(),
  codeSnippet: z.string().optional(),
  demoLink: z.string().url().optional(),
  // Metadata
  description: z.string().optional(),
  // Validation
  passed: z.boolean().optional(),
  reviewedAt: z.string().datetime().optional(),
  reviewNotes: z.string().optional(),
  // Timestamps
  submittedAt: z.string().datetime(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type ProjectSubmission = z.infer<typeof ProjectSubmissionSchema>;

/**
 * GitHub URL Validation Result
 * Result of HEAD request check to GitHub repository
 */
export const GitHubValidationResultSchema = z.object({
  isValid: z.boolean(),
  url: z.string().url(),
  status: z.number().optional(),
  owner: z.string().optional(),
  repo: z.string().optional(),
  branch: z.string().optional(),
  lastUpdated: z.string().datetime().optional(),
  error: z.string().optional(),
});

export type GitHubValidationResult = z.infer<typeof GitHubValidationResultSchema>;