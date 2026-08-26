import type { DiagnosticReport } from '@/types/api';

export type Step = 1 | 2 | 3 | 4 | 5;

export interface WizardState {
  step: Step;
  selectedRole: { title: string; career_field: string } | null;
  searchQuery: string;
  skillLevel: string;
  weeklyHours: number;
  format: string;
  language: string;
  freeContentOnly: boolean;
  assessmentQueued: boolean;
  answers: Record<string, number>;
  quizJobId?: string;
  aiQuizJobId?: string;
  analysis?: DiagnosticReport | null;
}

export const INITIAL_STATE: WizardState = {
  step: 1,
  selectedRole: null,
  searchQuery: '',
  skillLevel: 'intermediate',
  weeklyHours: 10,
  format: 'any',
  language: 'en',
  freeContentOnly: true,
  assessmentQueued: false,
  answers: {},
  quizJobId: undefined,
  aiQuizJobId: undefined,
  analysis: null,
};

export const ROLE_COLORS = [
  { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' },
  { bg: 'bg-emerald-100', text: 'text-emerald-700', border: 'border-emerald-200' },
  { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-200' },
  { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200' },
  { bg: 'bg-rose-100', text: 'text-rose-700', border: 'border-rose-200' },
  { bg: 'bg-cyan-100', text: 'text-cyan-700', border: 'border-cyan-200' },
];

export const LEVELS = ['beginner', 'intermediate', 'advanced', 'expert'] as const;
export const FORMATS = ['video', 'article', 'interactive', 'book', 'any'] as const;
export const LANGUAGES = ['en', 'ar'] as const;
