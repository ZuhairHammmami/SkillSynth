// المسار: src/frontend/src/context/AuthContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';
import axios from 'axios';

// 1. تعريف شكل بيانات المستخدم
interface User {
  email: string;
  full_name: string;
  id: number;
}

interface AuthState {
  token: string | null;
  user: User | null; // <-- إضافة بيانات المستخدم
  isAuthenticated: boolean;
  login: (token: string) => Promise<void>; // <-- ستصبح async
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  const fetchUser = async (currentToken: string) => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/users/me`,
        { headers: { Authorization: `Bearer ${currentToken}` } }
      );
      setUser(response.data);
    } catch (error) {
      console.error("Failed to fetch user", error);
      logout(); // إذا فشل جلب المستخدم (توكن منتهي الصلاحية)، سجله خروج
    }
  };

  useEffect(() => {
    const storedToken = Cookies.get('authToken');
    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken); // <-- جلب بيانات المستخدم عند تحميل الصفحة
    }
  }, []);

  const login = async (newToken: string) => {
    setToken(newToken);
    Cookies.set('authToken', newToken, { expires: 7, secure: true });
    await fetchUser(newToken); // <-- جلب بيانات المستخدم فور تسجيل الدخول
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    Cookies.remove('authToken');
  };

  const value = { token, user, isAuthenticated: !!token, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};