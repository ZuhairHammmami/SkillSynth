import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { toast } from 'sonner';

export interface Skill {
  id: string;
  name: string;
}

// 1. جلب المهارات
export const useSkills = () => {
  return useQuery({
    queryKey: ['admin-skills'],
    queryFn: async () => {
      const { data } = await apiClient.get<Skill[]>('/api/admin/skills');
      return data;
    },
  });
};

// 2. إنشاء مهارة
export const useCreateSkill = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (name: string) => {
      const { data } = await apiClient.post('/api/admin/skills', { name });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-skills'] });
      toast.success('تمت إضافة المهارة بنجاح');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل إضافة المهارة');
    }
  });
};

// 3. تحديث مهارة (الجديد)
export const useUpdateSkill = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, name }: { id: string; name: string }) => {
      const { data } = await apiClient.put(`/api/admin/skills/${id}`, { name });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-skills'] });
      toast.success('تم تحديث المهارة بنجاح');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل تحديث المهارة');
    }
  });
};

// 4. حذف مهارة
export const useDeleteSkill = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/admin/skills/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-skills'] });
      toast.success('تم حذف المهارة');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'لا يمكن حذف هذه المهارة');
    }
  });
};