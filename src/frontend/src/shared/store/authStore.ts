// src/shared/store/authStore.ts
/**
 * Session Store (Zustand)
 * 
 * Manages ONLY authentication session state (isAuthenticated, isLoading).
 * User profile data is managed exclusively by React Query (useUser hook).
 * 
 * This separation ensures:
 * - Single source of truth for each type of state
 * - React Query handles server data (profile, settings, etc.)
 * - Zustand handles session state (auth status, loading)
 * - No data duplication between stores
 */

import { create } from 'zustand';

// Re-export User type for backward compatibility
// Actual type is defined in src/entities/user
export type { User } from '@/entities/user';

interface SessionState {
  // Authentication state
  isAuthenticated: boolean;
  
  // Loading state (for session initialization)
  isLoading: boolean;
  
  // Actions
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  setIsLoading: (isLoading: boolean) => void;
  
  // Session cleanup on logout
  logout: () => void;
}

export const useAuthStore = create<SessionState>((set) => ({
  // Initial state
  isAuthenticated: false,
  isLoading: true, // Always start with loading=true for proper initialization
  
  // Actions to update state
  setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setIsLoading: (isLoading) => set({ isLoading }),
  
  // Logout action - clears session state
  // Note: React Query will handle clearing user data via query invalidation
  logout: () =>
    set({
      isAuthenticated: false,
      isLoading: false,
    }),
}));