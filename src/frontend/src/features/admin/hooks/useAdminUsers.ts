import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import type { User } from '@/shared/store/authStore';
import { toast } from 'sonner';

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

 // إضافة دالة التحديث
 export const useUpdateAdminUser = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, data }: { id: string, data: any }) => {
            const response = await apiClient.put(`/api/admin/users/${id}`, data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-users'] });
            toast.success('تم تحديث بيانات المستخدم بنجاح');
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'فشل تحديث المستخدم');
        }
    });
 };