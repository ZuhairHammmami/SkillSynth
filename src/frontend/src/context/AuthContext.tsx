// المسار: src/frontend/src/context/AuthContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';

// سنقوم بإزالة واجهة User مؤقتًا
// interface User { ... }

interface AuthState {
  // user: User | null; // <-- إزالة
  isAuthenticated: boolean;
  login: (token: string) => void; // <-- إزالة Promise
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  // const [user, setUser] = useState<User | null>(null); // <-- إزالة
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // الآن، سنتحقق فقط من وجود التوكن، بدون جلب بيانات المستخدم
    const token = Cookies.get('authToken');
    if (token) {
      setIsAuthenticated(true);
    }
    setIsLoading(false); // ننهي التحميل فورًا
  }, []);

  const login = (token: string) => {
    Cookies.set('authToken', token, { expires: 7, secure: true });
    setIsAuthenticated(true);
    // لم نعد بحاجة لجلب بيانات المستخدم من هنا
  };

  const logout = () => {
    Cookies.remove('authToken');
    // setUser(null); // <-- إزالة
    setIsAuthenticated(false);
  };

  const value = { isAuthenticated, login, logout, isLoading };

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