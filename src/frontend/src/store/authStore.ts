// المسار: src/store/authStore.ts
import { create } from 'zustand';

// تعريف شكل بيانات المستخدم الذي نتوقعه من الباك اند
export interface User {
  email: string;
  full_name: string;
  id: number;
  is_admin: boolean;
}

// تعريف شكل الحالة الكاملة للمصادقة
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  setIsLoading: (isLoading: boolean) => void;
  logout: () => void; // سنضيف منطق الكوكيز في الـ Hooks
}

export const useAuthStore = create<AuthState>((set) => ({
  // الحالة الأولية
  user: null,
  isAuthenticated: false,
  isLoading: true, // نبدأ دائمًا بالتحميل

  // الإجراءات (Actions) لتحديث الحالة
  setUser: (user) => set({ user }),
  setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setIsLoading: (isLoading) => set({ isLoading }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));