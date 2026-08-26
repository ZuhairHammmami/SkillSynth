'use client';

import { useMutation } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import type { AiJob, DiagnosticReport, ExplainPayload } from '@/types/api';

export function useGenerateWizardQuiz() {
  return useMutation({
    mutationFn: async (goal: string) => {
      const res = await apiClient.post<AiJob>('/ai/wizard-quiz', { goal });
      return res.data;
    },
  });
}

export function useWizardAnalysis() {
  return useMutation({
    mutationFn: async (input: {
      goal: string;
      weekly_hours: number;
      answers: Record<string, number>;
    }) => {
      const res = await apiClient.post<DiagnosticReport>(
        '/wizard/analysis',
        input
      );
      return res.data;
    },
  });
}

export function useGeneratePracticeTest() {
  return useMutation({
    mutationFn: async (input: { skill_id: number; n_questions: number }) => {
      const res = await apiClient.post<AiJob>('/ai/tests/generate', input);
      return res.data;
    },
  });
}

export function useExplainResult() {
  return useMutation({
    mutationFn: async (input: { assessment_id: number; answers: number[] }) => {
      const res = await apiClient.post<ExplainPayload>('/ai/explain', input);
      return res.data;
    },
  });
}
