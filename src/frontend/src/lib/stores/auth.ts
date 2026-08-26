/** Student auth state. Holds the profile and exposes the auth flows that call
 *  the FastAPI backend. The JWT lives in the `authToken` cookie (mirrors the
 *  previous Next.js client) so route guards and the API client can read it. */
import { writable } from 'svelte/store';
import { apiFetch } from '$lib/api/client';
import { getCookie, setCookie, deleteCookie } from '$lib/util';
import { invalidate } from '$lib/query';

export interface Profile {
  id: number;
  email: string;
  full_name: string | null;
  is_admin: boolean;
  created_at?: string;
}

export const authStore = writable<{ user: Profile | null; loading: boolean; initialized: boolean }>({
  user: null,
  loading: false,
  initialized: false
});

export function getAuthToken(): string | undefined {
  return getCookie('authToken');
}

export async function loadUser(): Promise<void> {
  authStore.update((s) => ({ ...s, loading: true }));
  try {
    const user = await apiFetch('/auth/me');
    authStore.set({ user, loading: false, initialized: true });
  } catch {
    authStore.set({ user: null, loading: false, initialized: true });
  }
}

export async function login(email: string, password: string): Promise<void> {
  const body = new URLSearchParams();
  body.set('username', email);
  body.set('password', password);
  const data = await apiFetch('/auth/token', {
    method: 'POST',
    body,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    token: null
  });
  setCookie('authToken', data.access_token, 1);
  await loadUser();
}

export async function register(email: string, password: string, fullName?: string): Promise<void> {
  await apiFetch('/auth/register', {
    method: 'POST',
    body: { email, password, full_name: fullName || null },
    token: null
  });
}

export async function forgotPassword(email: string): Promise<any> {
  return apiFetch('/auth/forgot-password', { method: 'POST', body: { email }, token: null });
}

export async function resetPassword(token: string, password: string): Promise<void> {
  await apiFetch('/auth/reset-password', { method: 'POST', body: { token, password }, token: null });
}

export async function changePassword(current: string, next: string): Promise<void> {
  await apiFetch('/auth/change-password', { method: 'POST', body: { current_password: current, new_password: next } });
}

export async function updateProfile(patch: { full_name?: string; email?: string }): Promise<void> {
  await apiFetch('/auth/me', { method: 'PUT', body: patch });
  await loadUser();
}

export function logout(): void {
  deleteCookie('authToken');
  invalidate(['paths']);
  invalidate(['dashboard']);
  invalidate(['analyticsDashboard']);
  invalidate(['skillGrowth']);
  authStore.set({ user: null, loading: false, initialized: true });
}
