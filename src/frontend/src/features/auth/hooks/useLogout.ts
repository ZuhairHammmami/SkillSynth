// المسار: src/features/auth/hooks/useLogout.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import Cookies from 'js-cookie';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

const logout = async () => {
  // لا يوجد طلب API هنا، فقط عمليات من جانب العميل
  Cookies.remove('authToken');
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      // تنظيف كل بيانات المستخدم المخزنة مؤقتًا في React Query
      queryClient.clear();
      toast.success("تم تسجيل خروجك بنجاح.");
      router.push('/login');
    },
  });
};