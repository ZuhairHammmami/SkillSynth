import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

const PUBLIC = ['/login', '/register', '/forgot-password', '/reset-password'];

/**
 * Runs on the server before rendering any (app) route, redirecting
 * unauthenticated visitors to the login page while avoiding redirect
 * loops on the public auth routes. This protects the SSR/first paint.
 */
export const load: LayoutServerLoad = ({ cookies, url }) => {
  const token = cookies.get('authToken');
  if (!token && !PUBLIC.includes(url.pathname)) {
    throw redirect(307, '/login');
  }
  return {};
};
