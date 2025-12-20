// المسار: src/features/user/hooks/useUser.ts
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import Cookies from 'js-cookie';
import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';

// تعريف شكل بيانات المستخدم الذي نتوقعه من GET /api/auth/users/me
interface User {
  email: string;
  full_name: string;
  id: number;
  is_admin: boolean;
}

/**
 * دالة الجلب (Fetcher Function): هذه هي الدالة الفعلية التي تتصل بالـ API.
 * React Query سيقوم باستدعائها تلقائيًا.
 */
const fetchUser = async (): Promise<User | null> => {
  // إذا لم يكن هناك توكن، فلا داعي لإرسال الطلب.
  const token = Cookies.get('authToken');
  if (!token) return null;

  try {
    const response = await apiClient.get<User>('/api/auth/users/me');
    return response.data;
  } catch (error) {
    // إذا فشل الطلب (توكن غير صالح)، قم بحذف الكوكي
    Cookies.remove('authToken');
    return null;
  }
};

/**
 * الـ Hook المخصص (Custom Hook): هذا هو ما سنستخدمه في مكوناتنا.
 * هو يغلف `useQuery` ويزوده بالمنطق اللازم.
 */
export const useUser = () => {
  // استدعاء useQuery لجلب بيانات المستخدم وتخزينها في ذاكرة التخزين المؤقت
  const { data: user, isLoading, isError, refetch } = useQuery<User | null>({
    queryKey: ['user'], // مفتاح فريد لتخزين هذه البيانات في ذاكرة React Query
    queryFn: fetchUser,
  });

  // الحصول على دوال التحديث من مخزن Zustand
  const { setUser, setIsAuthenticated, setIsLoading: setAuthIsLoading } = useAuthStore();

  // استخدام useEffect لمزامنة بيانات React Query مع مخزن Zustand
  useEffect(() => {
    setAuthIsLoading(isLoading);
    if (!isLoading) {
      setUser(user || null);
      setIsAuthenticated(!!user);
    }
  }, [user, isLoading, setUser, setIsAuthenticated, setAuthIsLoading]);

  return { user, isLoading, isError, refetch };
};