// Path Entity Types
export type PathStep = {
  id: string;
  path_id: string;
  step_number: number;
  title: string;
  content?: string;
  is_completed?: boolean;
  assessments?: Assessment[];
  resources?: Resource[];
};

export type Path = {
  id: string;
  profile_id?: string;
  title: string;
  description?: string;
  created_at: string;
  steps: PathStep[];
  skills?: Skill[];
  total_hours?: number;
  total_estimated_hours?: number;
};

export type Skill = {
  id: string;
  name: string;
  category?: string;
};

export type Resource = {
  id: string;
  title: string;
  url: string;
  type: string;
  is_free: boolean;
  is_official: boolean;
  author_or_platform?: string;
};

export type Assessment = {
  id: string;
  title: string;
  assessment_type: string;
  questions?: AssessmentQuestion[];
};

export type AssessmentQuestion = {
  id: string;
  title: string;
  question_text: string;
  options?: string[];
  correct_answer?: string;
  answer_type: 'multiple_choice' | 'short_answer' | 'essay';
};
