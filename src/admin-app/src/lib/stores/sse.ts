/** Live SSE connection to /api/realtime/admin/events (admin variant). Bridges
 *  server frames to the query cache and re-dispatches each as a DOM event so
 *  the activity ticker (Task 14) and other views can react. */
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
  if (type === 'path_generated') invalidate(['PATHS']);
  if (type === 'assessment_completed') invalidate(['ASMT']);
  if (browser) window.dispatchEvent(new CustomEvent('sse:' + type, { detail: data }));
}

export function connectSSE(): void {
  if (!browser || es) return;
  const token = getToken();
  if (!token) return;
  const BASE = (import.meta.env.PUBLIC_API_BASE_URL as string) || 'http://127.0.0.1:8000/api';
  es = new EventSource(`${BASE}/realtime/admin/events?token=${encodeURIComponent(token)}`);
  es.onopen = () => sseStatus.set('open');
  es.onerror = () => sseStatus.set('closed');
  ['path_generated', 'assessment_completed', 'connected', 'ping', 'activity'].forEach((f) => {
    es!.addEventListener(f, (e) => onFrame(f, safeParse((e as MessageEvent).data)));
  });
}

export function disconnectSSE(): void {
  if (es) { es.close(); es = null; }
  sseStatus.set('idle');
}
