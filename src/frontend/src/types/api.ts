export interface Profile {
  id: number;
  email: string;
  full_name?: string;
  is_admin: boolean;
  skill_profile?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface ProfileUpdate {
  full_name?: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  full_name?: string;
}

export interface Category {
  id: number;
  name: string;
  created_at?: string;
}

export interface Skill {
  id: number;
  name: string;
  description?: string;
  difficulty_level?: number;
  icon?: string;
  color?: string;
  categories?: Category[];
  prerequisites?: Skill[];
  resource_ids?: number[];
}

export interface SkillCreate {
  name: string;
  category_ids?: number[];
  prerequisite_ids?: number[];
  resource_ids?: number[];
}

export interface SkillUpdate {
  name?: string;
  description?: string;
  difficulty_level?: number;
  icon?: string;
  color?: string;
  category_ids?: number[];
  prerequisite_ids?: number[];
  resource_ids?: number[];
}

export interface Resource {
  id: number;
  title: string;
  url: string;
  type: string;
  is_free?: boolean;
  is_official?: boolean;
  author_or_platform?: string;
  language?: string;
}

export interface ResourceCreate {
  title: string;
  url: string;
  type: string;
  is_free?: boolean;
  is_official?: boolean;
  author_or_platform?: string;
  language?: string;
}

export interface ResourceUpdate {
  title?: string;
  url?: string;
  type?: string;
  is_free?: boolean;
  is_official?: boolean;
  author_or_platform?: string;
  language?: string;
}

export interface JobRole {
  id: number;
  title: string;
  description?: string;
  career_field?: string;
  skills?: Skill[];
}

export interface JobRoleCreate {
  title: string;
  description?: string;
  career_field?: string;
  skill_ids?: number[];
}

export interface JobRoleUpdate {
  title?: string;
  description?: string;
  career_field?: string;
  skill_ids?: number[];
}

export interface PathStep {
  id: number;
  step_number: number;
  title: string;
  content?: string;
  resource_ids?: number[];
  assessment_ids?: number[];
  is_completed?: boolean;
}

export interface Path {
  id: number;
  profile_id: number;
  title: string;
  description?: string;
  total_estimated_hours?: number;
  total_estimated_weeks?: number;
  goal_job_role?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  steps: PathStep[];
  skills?: Skill[];
  skill_ids?: number[];
}

export interface GeneratePathInput {
  goal: string;
  weekly_hours: number;
  preferences: { is_free?: boolean; format?: string; language?: string };
  answers: Record<string, number>;
}

export interface DashboardProgress {
  total_paths: number;
  total_steps: number;
  completed_steps: number;
  completion_percentage: number;
  total_hours: number;
  remaining_hours: number;
}

export interface AnalyticsDashboard {
  total_paths?: number;
  completed_steps?: number;
  completion_rate?: number;
  mastered_skills?: number;
  learning_skills?: number;
  total_skill_areas?: number;
  learning_velocity?: number;
  recent_activity?: unknown[];
}

export interface Assessment {
  id: number;
  title: string;
  assessment_type: string;
  questions?: unknown[];
}

export interface AssessmentResult {
  id: number;
  profile_id: number;
  assessment_id: number;
  score?: number;
  total_questions?: number;
  responses?: unknown;
  submitted_at?: string;
}

export interface AdminDashboard {
  user_activity: {
    total_users: number;
    new_users_last_24h: number;
    new_users_last_7d: number;
    users_with_paths: number;
  };
  content_engagement: {
    total_paths: number;
    total_steps: number;
    total_completions: number;
    most_completed_steps: unknown[];
  };
  system_health: {
    database_status: string;
    total_users: number;
    total_paths: number;
    total_assessments: number;
    api_version: string;
  };
  most_active_users: { user_email: string; completed_steps: number }[];
  most_requested_skills: { skill_name: string; path_count: number }[];
  total_hours_learned: number;
  average_completion_rate: number;
  total_assessment_attempts: number;
  average_assessment_score: number;
}

export interface WizardOptions {
  job_roles: { title: string; description?: string; career_field: string }[];
  career_fields: Record<string, { title: string; description?: string; career_field: string }[]>;
  preferences: { formats: string[]; languages: string[] };
}

export interface AiJob {
  job_id: string;
}

export interface PerSkillResult {
  skill: string;
  skill_id: number;
  correct: number;
  total: number;
  answered_count: number;
  assessed_level: number;
  previous_level: number;
  gap_to_mastery: number;
  weakness: boolean;
}

export interface WeaknessEntry {
  skill_id: number;
  skill_name: string;
  current_level: number;
  difficulty?: number;
  gap?: number;
}

export interface DiagnosticReport {
  per_skill: PerSkillResult[];
  weaknesses: string[];
  strengths: string[];
  recommended_focus: string[];
  estimated_weeks: number;
  narrative: string | null;
  narrative_available: boolean;
}

export interface LearningAnalysis {
  weaknesses: WeaknessEntry[];
  strengths: WeaknessEntry[];
  weakness_count: number;
  strength_count: number;
  total_skills_assessed: number;
  average_assessment_score: number;
  total_assessments_taken: number;
  recommended_focus: string[];
}

export interface ExplainPayload {
  explanations: { question_index: number; why: string }[];
  advice: string;
  narrative_available: boolean;
}
