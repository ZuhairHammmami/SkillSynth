'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { queryKeys } from '@/shared/api/query-keys';
import type { Profile, ProfileUpdate, PasswordChange, TokenResponse, RegisterInput } from '@/types/api';
import Cookies from 'js-cookie';

const TOKEN_COOKIE = 'authToken';

export function useAuth() {
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      const res = await apiClient.post<TokenResponse>('/auth/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      return res.data;
    },
    onSuccess: (data) => {
      Cookies.set(TOKEN_COOKIE, data.access_token, { expires: 7, path: '/' });
      queryClient.invalidateQueries({ queryKey: queryKeys.compat.profile() });
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (input: RegisterInput) => {
      const res = await apiClient.post<Profile>('/auth/register', input);
      return res.data;
    },
  });

  const logout = () => {
    Cookies.remove(TOKEN_COOKIE);
    queryClient.clear();
  };

  return { loginMutation, registerMutation, logout };
}

export function useProfile() {
  return useQuery({
    queryKey: queryKeys.compat.profile(),
    queryFn: async () => {
      const res = await apiClient.get<Profile>('/auth/me');
      return res.data;
    },
    retry: false,
    staleTime: 1000 * 60,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: ProfileUpdate) => {
      const res = await apiClient.put<Profile>('/auth/me', data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['profile'] }),
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: async (data: PasswordChange) => {
      const res = await apiClient.post('/auth/change-password', data);
      return res.data;
    },
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: async (email: string) => {
      const res = await apiClient.post('/auth/forgot-password', { email });
      return res.data;
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: async (data: { token: string; new_password: string }) => {
      const res = await apiClient.post('/auth/reset-password', data);
      return res.data;
    },
  });
}
