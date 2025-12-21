// المسار: src/features/admin/hooks/useAdminUsers.ts
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import type { User } from '@/store/authStore'; // إعادة استخدام نفس تعريف المستخدم

const fetchUsers = async (): Promise<User[]> => {
     const { data } = await apiClient.get<User[]>('/api/admin/users');
     return data;
 };

 export const useAdminUsers = () => {
     return useQuery({
         queryKey: ['admin-users'],
         queryFn: fetchUsers,
     });
 };