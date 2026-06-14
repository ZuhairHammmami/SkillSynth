import { z } from "zod";

// Assessment Entity Types
export type AssessmentResult = {
  id: number;
  profile_id: number;
  assessment_id: number;
  score: number;
  submitted_at: string;
  answers?: AssessmentAnswer[];
};

export type AssessmentAnswer = {
  question_id: number;
  answer: string;
  is_correct?: boolean;
};

export type AssessmentProgress = {
  total_questions: number;
  answered_questions: number;
  correct_answers: number;
  score_percentage: number;
};

export type AssessmentStats = {
  total_assessments: number;
  completed_assessments: number;
  average_score: number;
  last_assessment_date?: string;
};

// Quiz Question Type
export type QuizQuestion = {
  id: string;
  conceptId: string;
  questionText: string;
  questionType: "multiple-choice" | "short-answer" | "code-snippet" | "true-false";
  difficulty: "beginner" | "intermediate" | "advanced";
  options?: string[];
  correctAnswer: string;
  explanation: string;
  estimatedTimeSeconds: number;
  createdAt: string;
};

// Assessment Type
export type Assessment = {
  id: string;
  conceptId: string;
  userId: string;
  title: string;
  description: string;
  questions: QuizQuestion[];
  totalTimeEstimateSeconds: number;
  passingScore: number;
  difficulty: "beginner" | "intermediate" | "advanced";
  createdAt: string;
  expiresAt: string;
};

// Submit Assessment Type
export type SubmitAssessment = {
  assessmentId: string;
  userId: string;
  answers: Record<string, string>;
  submittedAt: string;
  timeSpentSeconds?: number;
};

// Create Assessment Request Type
export type CreateAssessmentRequest = {
  conceptId: string;
  userId: string;
  difficulty?: "beginner" | "intermediate" | "advanced";
  previousAttempts?: number;
};

// Skill Gap Type
export type SkillGap = {
  conceptId: string;
  gapScore: number;
  recommendedResources: string[];
  prerequisitesNeeded: string[];
  id?: string;
  blockedAdvancedSkills?: string[];
  userId?: string;
  weakSkillId?: string;
  reliabilityScore?: number;
  lastAssessmentDate?: string | null;
  recommendationStatus?: string;
  createdAt?: string;
  updatedAt?: string;
};

// Stuck Tracking Type
export type StuckTracking = {
  userId: string;
  conceptId: string;
  stuckCount: number;
  stuckTime: string;
  triggers: string[];
  nodeStartTime?: string;
};

// Learning Intervention Type
export type LearningIntervention = {
  id: string;
  userId: string;
  conceptId: string;
  interventionType: "hint" | "alternative-explanation" | "prerequisite-review" | "break-recommendation";
  content: string;
  createdAt: string;
  triggerReason?: string;
  hoursSpent?: number;
  failedAttempts?: number;
  interventionAccepted?: boolean;
  actionTaken?: string;
};

// Zod Schemas
export const QuizQuestionSchema = z.object({
  id: z.string().uuid(),
  conceptId: z.string(),
  questionText: z.string(),
  questionType: z.enum(["multiple-choice", "short-answer", "code-snippet", "true-false"]),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]),
  options: z.array(z.string()).optional(),
  correctAnswer: z.string(),
  explanation: z.string(),
  estimatedTimeSeconds: z.number(),
  createdAt: z.string().datetime(),
});

export const AssessmentSchema = z.object({
  id: z.string().uuid(),
  conceptId: z.string(),
  userId: z.string(),
  title: z.string(),
  description: z.string(),
  questions: z.array(QuizQuestionSchema),
  totalTimeEstimateSeconds: z.number(),
  passingScore: z.number(),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]),
  createdAt: z.string().datetime(),
  expiresAt: z.string().datetime(),
});

export const AssessmentResultSchema = z.object({
  id: z.number(),
  profile_id: z.number(),
  assessment_id: z.number(),
  score: z.number(),
  submitted_at: z.string().datetime(),
  answers: z.array(z.object({
    question_id: z.number(),
    answer: z.string(),
    is_correct: z.boolean().optional(),
  })).optional(),
});

export const SubmitAssessmentSchema = z.object({
  assessmentId: z.string(),
  userId: z.string(),
  answers: z.record(z.string(), z.string()),
  submittedAt: z.string().datetime(),
  timeSpentSeconds: z.number().optional(),
});

export const CreateAssessmentRequestSchema = z.object({
  conceptId: z.string(),
  userId: z.string(),
  difficulty: z.enum(["beginner", "intermediate", "advanced"]).optional(),
  previousAttempts: z.number().optional(),
});

export const SkillGapSchema = z.object({
  conceptId: z.string(),
  gapScore: z.number(),
  recommendedResources: z.array(z.string()),
  prerequisitesNeeded: z.array(z.string()),
  id: z.string().optional(),
  blockedAdvancedSkills: z.array(z.string()).optional(),
  userId: z.string().optional(),
  weakSkillId: z.string().optional(),
  reliabilityScore: z.number().optional(),
  lastAssessmentDate: z.string().nullable().optional(),
  recommendationStatus: z.string().optional(),
  createdAt: z.string().optional(),
  updatedAt: z.string().optional(),
});

export const StuckTrackingSchema = z.object({
  userId: z.string(),
  conceptId: z.string(),
  stuckCount: z.number(),
  stuckTime: z.string().datetime(),
  triggers: z.array(z.string()),
  nodeStartTime: z.string().optional(),
});

export const LearningInterventionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string(),
  conceptId: z.string(),
  interventionType: z.enum(["hint", "alternative-explanation", "prerequisite-review", "break-recommendation"]),
  content: z.string(),
  createdAt: z.string().datetime(),
});
