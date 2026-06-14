/**
 * src/lib/supabase.ts
 * 
 * Supabase Client Configuration
 * Initializes the Supabase client for frontend authentication and database access
 */

import { createBrowserClient } from "@supabase/ssr";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    "Missing Supabase environment variables: NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY"
  );
}

/**
 * Initialize Supabase browser client
 * Used for client-side authentication and database queries with RLS
 */
export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey);

/**
 * Get current authenticated user from Supabase
 * Returns the auth.uid() from Supabase auth
 */
export async function getCurrentUser() {
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (error || !user) {
    return null;
  }

  return user;
}

/**
 * Sign out the current user
 */
export async function signOut() {
  return await supabase.auth.signOut();
}
