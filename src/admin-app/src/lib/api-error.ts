import axios from 'axios';

/** Shape of a 409 restricted-delete detail body from the backend. */
export interface DependentsConflict {
  message?: string;
  dependents?: Record<string, number>;
}

export function getApiErrorMessage(error: unknown, fallback = 'Request failed'): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { detail?: unknown } | undefined;
    if (typeof data?.detail === 'string') return data.detail;
    if (data?.detail) return JSON.stringify(data.detail);
  }
  return fallback;
}

export function getDependentsConflict(error: unknown): DependentsConflict | null {
  if (axios.isAxiosError(error) && error.response?.status === 409) {
    const detail = (error.response.data as { detail?: unknown } | undefined)?.detail;
    if (detail && typeof detail === 'object' && 'dependents' in detail) {
      return detail as DependentsConflict;
    }
  }
  return null;
}