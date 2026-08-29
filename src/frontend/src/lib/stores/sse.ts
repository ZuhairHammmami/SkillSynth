/** Live SSE connection to /api/realtime/events. Bridges server frames to the
 *  query cache (invalidating the same keys the previous React Query layer used)
 *  and re-dispatches each frame as a DOM CustomEvent (`sse:<frame>`) so view
 *  components (wizard quiz, proficiency badge) can react. */
import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { getToken } from '$lib/api/client';
import { invalidate } from '$lib/query';

export const sseStatus = writable<'idle' | 'open' | 'closed'>('idle');

let es: EventSource | null = null;

function safeParse(d: string): any {
  try { return JSON.parse(d); } catch { return d; }
}

function onFrame(type: string, data: any): void {
  if (type === 'path_generated') {
    invalidate(['paths']);
    invalidate(['dashboard']);
  } else if (type === 'assessment_completed') {
    invalidate(['analyticsDashboard']);
  } else if (type === 'ai_test_ready' || type === 'ai_quiz_ready' ||
      type === 'ai_step_quiz_ready') {
    invalidate(['paths']);
    invalidate(['dashboard']);
    invalidate(['analyticsDashboard']);
  } else if (type === 'ai_step_diagnostic' || type === 'proficiency_adjusted') {
    invalidate(['dashboard']);
    invalidate(['analyticsDashboard']);
  }
  if (browser) window.dispatchEvent(new CustomEvent('sse:' + type, { detail: data }));
}

export function connectSSE(): void {
  if (!browser || es) return;
  const token = getToken();
  if (!token) return;
  const BASE = (import.meta.env.PUBLIC_API_BASE_URL as string) || 'http://127.0.0.1:8000/api';
  es = new EventSource(`${BASE}/realtime/events?token=${encodeURIComponent(token)}`);
  es.onopen = () => sseStatus.set('open');
  es.onerror = () => sseStatus.set('closed');
  const frames = [
    'path_generated', 'assessment_completed', 'ai_quiz_ready',
    'ai_quiz_failed', 'ai_test_ready', 'ai_test_failed',
    'ai_step_quiz_ready', 'ai_step_diagnostic', 'proficiency_adjusted',
    'proficiency_review_failed',
    'connected', 'ping'
  ];
  frames.forEach((f) => {
    es!.addEventListener(f, (e) => onFrame(f, safeParse((e as MessageEvent).data)));
  });
  sseStatus.set('idle');
}

export function disconnectSSE(): void {
  if (es) { es.close(); es = null; }
  sseStatus.set('idle');
}
