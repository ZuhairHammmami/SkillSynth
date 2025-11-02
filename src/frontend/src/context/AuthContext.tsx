// المسار: src/frontend/src/context/AuthContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// تعريف أنواع البيانات التي سنحتفظ بها
interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

// إنشاء السياق بقيمة ابتدائية
const AuthContext = createContext<AuthState | undefined>(undefined);

// إنشاء المزود (Provider) الذي سيحتوي على المنطق
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);

  // عند تحميل التطبيق، تحقق مما إذا كان هناك توكن محفوظ في localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('authToken', newToken); // احفظ التوكن للاستخدام لاحقًا
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('authToken'); // احذف التوكن عند تسجيل الخروج
  };

  const value = {
    token,
    isAuthenticated: !!token, // será `true` si el token existe
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// إنشاء "خطاف" (Hook) مخصص ليسهل الوصول إلى السياق
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};