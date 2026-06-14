'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import Cookies from 'js-cookie';
import { useAuthStore } from '@/shared/store/authStore';
import { useEffect } from 'react';
import { User } from '@/entities/user';
import { queryKeys } from '@/shared/api/query-keys';

const fetchUser = async (): Promise<User | null> => {
  const token = Cookies.get('authToken');
  if (!token) return null;

  try {
    const response = await apiClient.get<User>('/api/auth/users/me');
    return response.data;
  } catch (error) {
    Cookies.remove('authToken');
    return null;
  }
};

export const useUser = () => {
  const { data: user, isLoading, isError } = useQuery<User | null>({
    queryKey: queryKeys.user.current(),
    queryFn: fetchUser,
  });

  const { setIsAuthenticated, setIsLoading: setAuthIsLoading } = useAuthStore();

  useEffect(() => {
    setAuthIsLoading(isLoading);
    if (!isLoading) {
      setIsAuthenticated(!!user);
    }
  }, [user, isLoading, setIsAuthenticated, setAuthIsLoading]);

  return {
    user,
    isLoading,
    isError,
  };
};
