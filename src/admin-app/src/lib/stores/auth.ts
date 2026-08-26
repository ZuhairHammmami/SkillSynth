/** Admin auth state. Mirrors the student store but enforces the `is_admin`
 *  gate: if /auth/me returns a non-admin, the token is dropped and login
 *  rejects. The JWT lives in the `adminToken` cookie. */
import { writable } from 'svelte/store';
import { apiFetch } from '$lib/api/client';
import { getCookie, setCookie, deleteCookie } from '$lib/util';
import { invalidate } from '$lib/query';
import type { Profile } from '$lib/types/api';

export interface AdminProfile extends Profile {
  is_admin: boolean;
}

export const authStore = writable<{ user: AdminProfile | null; loading: boolean; initialized: boolean }>({
  user: null,
  loading: false,
  initialized: false
});

export function getAdminToken(): string | undefined {
  return getCookie('adminToken');
}

export async function fetchProfile(): Promise<AdminProfile> {
  const user = (await apiFetch('/auth/me')) as AdminProfile;
  if (!user.is_admin) {
    deleteCookie('adminToken');
    throw new Error('Not an administrator');
  }
  return user;
}

export async function loadUser(): Promise<void> {
  authStore.update((s) => ({ ...s, loading: true }));
  try {
    const user = await fetchProfile();
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
  setCookie('adminToken', data.access_token, 1);
  await loadUser();
}

export async function changePassword(current: string, next: string): Promise<void> {
  await apiFetch('/auth/change-password', { method: 'POST', body: { current_password: current, new_password: next } });
}

export function logout(): void {
  deleteCookie('adminToken');
  invalidate(['adminUsers']);
  invalidate(['adminDashboard']);
  authStore.set({ user: null, loading: false, initialized: true });
}
