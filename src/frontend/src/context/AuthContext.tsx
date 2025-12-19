// المسار: src/context/AuthContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';
import apiClient from '@/lib/api';

interface User {
  email: string;
  full_name: string;
  id: number;
  is_admin: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  refetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUser = async () => {
    const token = Cookies.get('authToken');
    if (!token) {
      setIsLoading(false);
      return;
    }
    try {
      // =====> هذا هو التصحيح الحاسم <=====
      const response = await apiClient.get<User>('/api/auth/users/me');
      // ===================================
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      console.error("Failed to fetch user, logging out.", error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (token: string) => {
    Cookies.set('authToken', token, { expires: 7 });
    await fetchUser();
  };

  const logout = () => {
    Cookies.remove('authToken');
    setUser(null);
    setIsAuthenticated(false);
  };

  const refetchUser = async () => {
      await fetchUser();
  }

  const value = { user, isAuthenticated, login, logout, isLoading, refetchUser };

  return (
    <AuthContext.Provider value={value}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};