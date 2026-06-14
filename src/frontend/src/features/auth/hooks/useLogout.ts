import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import Cookies from 'js-cookie';
import { useAuthStore } from '@/shared/store/authStore';
import { queryKeys } from '@/shared/api/query-keys';

export const useLogout = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { logout: clearSession } = useAuthStore();

  return useMutation({
    mutationFn: async () => {
      Cookies.remove('authToken', { path: '/' });
    },
    onSuccess: () => {
      clearSession();
      queryClient.invalidateQueries({ queryKey: queryKeys.user.all });
      queryClient.clear();
      toast.success("تم تسجيل خروجك بنجاح.");
      router.push('/login');
    },
    onError: (error: any) => {
      toast.error(error.message || 'فشل تسجيل الخروج.');
    },
  });
};
