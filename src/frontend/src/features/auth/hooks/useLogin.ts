import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import Cookies from 'js-cookie';
import apiClient from '@/shared/lib/api';
import { queryKeys } from '@/shared/api/query-keys';
import { useAuthStore } from '@/shared/store/authStore';
import type { User } from '@/entities/user';

interface LoginCredentials {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const useLogin = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { setIsAuthenticated } = useAuthStore();

  return useMutation({
    mutationFn: async (credentials: LoginCredentials): Promise<User> => {
      const formData = new URLSearchParams();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const tokenResponse = await apiClient.post<TokenResponse>(
        '/api/auth/token',
        formData.toString(),
        {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }
      );

      const { access_token } = tokenResponse.data;

      Cookies.set('authToken', access_token, {
        expires: 7,
        path: '/',
        sameSite: 'lax',
      });

      const userResponse = await apiClient.get<User>('/api/auth/users/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      return userResponse.data;
    },
    onSuccess: (user) => {
      toast.success("مرحباً بعودتك!", { description: "تم تسجيل دخولك بنجاح." });

      queryClient.invalidateQueries({ queryKey: queryKeys.user.all });
      setIsAuthenticated(true);

      if (user.is_admin) {
        router.push('/admin/dashboard');
      } else {
        router.push('/dashboard');
      }
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || error.message || 'فشل تسجيل الدخول. تأكد من بياناتك.';
      toast.error(message);
      Cookies.remove('authToken', { path: '/' });
    },
  });
};
