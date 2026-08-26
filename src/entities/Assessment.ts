import { z } from "zod";

/**
 * Quiz Question Schema
 * Represents a single question in an adaptive assessment
 */
export const QuizQuestionSchema = z.object({
  id: z.string().uuid(),
  conceptId: z.string().uuid(),
  questionText: z.string().min(10),
  questionType: z.enum(["multiple-choice", "short-answer", "code-snippet", "true-false"]),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]),
  options: z.array(z.string()).optional(), // For multiple-choice questions
  correctAnswer: z.string(),
  explanation: z.string().describe("Why this answer is correct"),
  relatedPrerequisites: z.array(z.string().uuid()).optional(),
  estimatedTimeSeconds: z.number().positive(),
  createdAt: z.string().datetime(),
});

export type QuizQuestion = z.infer<typeof QuizQuestionSchema>;

/**
 * Assessment Result Schema
 * Tracks user performance on a quiz/assessment for a specific concept
 */
export const AssessmentResultSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  conceptId: z.string().uuid(),
  score: z.number().min(0).max(100).describe("Percentage score (0-100)"),
  totalQuestions: z.number().positive(),
  correctAnswers: z.number().nonnegative(),
  attemptNumber: z.number().positive(),
  passed: z.boolean().describe("True if score >= 80%"),
  timeSpentSeconds: z.number().nonnegative(),
  answers: z.record(z.string(), z.string()).optional().describe("Question ID -> User's answer"),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type AssessmentResult = z.infer<typeof AssessmentResultSchema>;

/**
 * Assessment Schema
 * Dynamic quiz tailored to a concept and user's mastery level
 */
export const AssessmentSchema = z.object({
  id: z.string().uuid(),
  conceptId: z.string().uuid(),
  userId: z.string().uuid(),
  title: z.string(),
  description: z.string(),
  questions: z.array(QuizQuestionSchema),
  totalTimeEstimateSeconds: z.number().positive(),
  passingScore: z.number().min(70).max(100).default(80),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]),
  prerequisites: z.array(z.string().uuid()).optional(),
  createdAt: z.string().datetime(),
  expiresAt: z.string().datetime().optional(),
});

export type Assessment = z.infer<typeof AssessmentSchema>;

/**
 * Assessment Request/Response Schema
 * Used for API communication
 */
export const CreateAssessmentRequestSchema = z.object({
  conceptId: z.string().uuid(),
  userId: z.string().uuid(),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]).optional(),
});

export type CreateAssessmentRequest = z.infer<typeof CreateAssessmentRequestSchema>;

/**
 * Submit Assessment Schema
 * User submitting answers to an assessment
 */
export const SubmitAssessmentSchema = z.object({
  assessmentId: z.string().uuid(),
  userId: z.string().uuid(),
  answers: z.record(z.string(), z.string()).describe("Question ID -> User's answer"),
  timeSpentSeconds: z.number().nonnegative(),
});

export type SubmitAssessment = z.infer<typeof SubmitAssessmentSchema>;

/**
 * Alternative Explanation Schema
 * LLM-generated explanations for struggling learners (Phase 3.4 & 4.0)
 * 
 * Phase 4.0 Addition: Tracks which provider (local/openai) generated the explanation
 * for cost and privacy analysis
 */
export const AlternativeExplanationSchema = z.object({
  id: z.string().uuid(),
  conceptId: z.string().uuid(),
  generatedByUserId: z.string().uuid().nullable(),
  explanationText: z.string().min(50),
  difficultyLevel: z.enum(["beginner", "intermediate", "advanced"]),
  prerequisitesConsidered: z.array(z.string().uuid()),
  qualityScore: z.number().min(0).max(1).optional(),
  modelUsed: z.string().default("openai-gpt-4").describe("e.g., gpt-4, mistral, llama3"),
  provider: z.enum(["openai", "local"]).describe("Provider that generated this explanation (Phase 4.0)"),
  generationTimeMs: z.number().nonnegative().optional().describe("Time taken to generate explanation"),
  costEstimate: z.number().nonnegative().optional().describe("Estimated cost in USD (OpenAI only)"),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type AlternativeExplanation = z.infer<typeof AlternativeExplanationSchema>;

/**
 * Skill Gap Schema
 * Identifies weak prerequisites that block advanced learning
 */
export const SkillGapSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  weakSkillId: z.string().uuid(),
  blockedAdvancedSkills: z.array(z.string().uuid()),
  reliabilityScore: z.number().min(0).max(1),
  lastAssessmentDate: z.string().datetime().nullable(),
  recommendationStatus: z.enum(["pending", "recommended", "in_progress", "resolved"]),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type SkillGap = z.infer<typeof SkillGapSchema>;

/**
 * Learning Intervention Schema
 * Represents an intervention triggered when user is stuck
 */
export const LearningInterventionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  conceptId: z.string().uuid(),
  interventionType: z.enum(["learning_intervention", "skip_option", "alternative_path"]),
  triggerReason: z.enum(["stuck_48h", "repeated_failures", "skill_gap"]),
  hoursSpent: z.number().nonnegative(),
  failedAttempts: z.number().nonnegative(),
  interventionAccepted: z.boolean().optional(),
  actionTaken: z.string().optional(),
  createdAt: z.string().datetime(),
});

export type LearningIntervention = z.infer<typeof LearningInterventionSchema>;

/**
 * Stuck Tracking Schema
 * Monitors time spent on a node without completion
 */
export const StuckTrackingSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  conceptId: z.string().uuid(),
  nodeStartTime: z.string().datetime(),
  hoursElapsed: z.number().nonnegative(),
  interventionTriggered: z.boolean().default(false),
  interventionTriggeredAt: z.string().datetime().nullable().optional(),
  interventionType: z.enum(["learning_intervention", "skip_option", "alternative_path"]).nullable().optional(),
  simplifiedSubpath: z.array(z.string().uuid()).optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type StuckTracking = z.infer<typeof StuckTrackingSchema>;
