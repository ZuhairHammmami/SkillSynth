'use client';

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import apiClient from './api';
import Cookies from 'js-cookie';

interface Profile {
  id: number;
  email: string;
  full_name?: string;
  is_admin: boolean;
  role_id?: number;
}

interface AuthContextType {
  profile: Profile | null;
  isLoading: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchProfile = useCallback(async () => {
    const token = Cookies.get('adminToken');
    if (!token) {
      setProfile(null);
      setIsLoading(false);
      return;
    }
    try {
      const res = await apiClient.get<Profile>('/auth/me');
      if (!res.data.is_admin) {
        Cookies.remove('adminToken');
        setProfile(null);
      } else {
        setProfile(res.data);
      }
    } catch {
      Cookies.remove('adminToken');
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchProfile(); }, [fetchProfile]);

  const login = useCallback(async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    const res = await apiClient.post<{ access_token: string; token_type: string }>(
      '/auth/token', formData,
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );
    Cookies.set('adminToken', res.data.access_token, { expires: 1, path: '/' });
    await fetchProfile();
  }, [fetchProfile]);

  const logout = useCallback(() => {
    Cookies.remove('adminToken');
    setProfile(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    await fetchProfile();
  }, [fetchProfile]);

  return (
    <AuthContext.Provider value={{
      profile, isLoading, isAdmin: profile?.is_admin ?? false,
      login, logout, refreshProfile,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
