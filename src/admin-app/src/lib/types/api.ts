/** Domain DTOs for the SkillSynth API. Kept pragmatic: known fields are typed,
 *  unknown/extensible payloads allow extra properties so pages can evolve. */

export interface Profile {
  id: number;
  email: string;
  full_name: string | null;
  is_admin: boolean;
  created_at?: string;
}

export interface Step {
  id: number;
  path_id: number;
  title: string;
  description?: string | null;
  order_index?: number;
  completed?: boolean;
  duration_hours?: number;
  skill?: { id: number; name: string } | null;
  resource_ids?: number[];
  assessment_ids?: number[];
}

export interface Path {
  id: number;
  title: string;
  goal: string;
  user_id?: number;
  created_at?: string;
  status?: string;
  progress?: number;
  steps?: Step[];
  [key: string]: any;
}

export interface DashboardStats {
  completion_rate?: number;
  learning_hours?: number;
  paths_count?: number;
  completed_steps?: number;
  total_steps?: number;
  recent_activity?: any[];
  [key: string]: any;
}

export interface SkillGrowthItem {
  skill: string;
  proficiency: number;
  status: 'mastered' | 'learning' | 'not_started' | string;
}

export interface WizardOptions {
  job_roles: { id: number; title: string }[];
  level: string[];
  format: string[];
  language: string[];
  free: boolean;
  [key: string]: any;
}

export interface AssessmentQuestion {
  id: number;
  skill_id: number;
  question: string;
  options: { id: string; text: string }[];
  [key: string]: any;
}

export interface AnalyticsDashboard {
  mastered_skills?: number;
  learning_velocity?: number;
  [key: string]: any;
}

export interface LearningAnalysis {
  weaknesses: { skill: string; score: number }[];
  strengths: { skill: string; score: number }[];
  [key: string]: any;
}

/* ---- Admin domain ---- */
export interface AdminUser {
  id: number;
  email: string;
  full_name: string | null;
  is_admin: boolean;
  created_at?: string;
}
export interface Category {
  id: number;
  name: string;
  description?: string | null;
  parent_id?: number | null;
}
export interface Skill {
  id: number;
  name: string;
  description?: string | null;
  difficulty_level?: number;
  estimated_hours?: number;
  category_id?: number | null;
  category_ids?: number[];
  prerequisite_ids?: number[];
}
export interface Resource {
  id: number;
  title: string;
  url: string;
  type?: string;
  language?: string;
  is_free?: boolean;
  author_or_platform?: string | null;
  skill_id?: number | null;
}
export interface JobRole {
  id: number;
  title: string;
  description?: string | null;
  career_field?: string;
  skill_ids?: number[];
}
export interface Assessment {
  id: number;
  title: string;
  type?: string;
  passing_score?: number;
  time_limit?: number;
}
export interface EventLog {
  id: number;
  created_at: string;
  category: string;
  action: string;
  user?: string | null;
  entity?: string | null;
}
export interface AdminDashboard {
  user_activity?: any;
  content_engagement?: any;
  system_health?: any;
  most_active_users?: any[];
  most_requested_skills?: any[];
  total_hours_learned?: number;
  average_completion_rate?: number;
  total_assessment_attempts?: number;
  average_assessment_score?: number;
}
export interface FeatureFlags {
  ai_enabled: boolean;
  [key: string]: any;
}
export interface Backup {
  path: string;
  size?: number;
  created_at?: string;
}
export interface DbTable {
  name: string;
  row_count?: number;
  columns?: { name: string; type: string; nullable: boolean; pk: boolean }[];
}
export interface DbInspector {
  size_bytes?: number;
  table_count?: number;
  tables?: DbTable[];
  [key: string]: any;
}
