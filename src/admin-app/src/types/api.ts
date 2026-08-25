export interface Profile {
  id: number;
  email: string;
  full_name?: string;
  is_admin: boolean;
  created_at?: string;
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

export interface JobRole {
  id: number;
  title: string;
  description?: string;
  career_field?: string;
  skills?: Skill[];
}

export interface Assessment {
  id: number;
  skill_id?: number;
  title: string;
  type: string;
  assessment_type: string;
  questions?: unknown[];
  passing_score?: number;
  time_limit_minutes?: number;
  created_at?: string;
}

export interface AssessmentResult {
  id: number;
  profile_id: number;
  assessment_id: number;
  score?: number;
  total_questions?: number;
  submitted_at?: string;
  profile?: { email?: string; full_name?: string };
  assessment?: { title?: string; assessment_type?: string };
}

export interface Path {
  id: number;
  profile_id: number;
  title: string;
  description?: string;
  total_estimated_hours?: number;
  status?: string;
  created_at?: string;
  user_email?: string;
}

export interface Event {
  id: number;
  profile_id?: number;
  category: string;
  action: string;
  entity_type?: string;
  entity_id?: number;
  data?: Record<string, unknown>;
  ip_address?: string;
  created_at?: string;
  user?: { full_name?: string; email?: string; is_admin?: boolean };
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
