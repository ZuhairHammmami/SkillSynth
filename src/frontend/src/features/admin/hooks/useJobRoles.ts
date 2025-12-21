import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';

export interface JobRole {
  id: number;
  title: string;
}

// 1. جلب الأدوار
export const useJobRoles = () => {
  return useQuery({
    queryKey: ['admin-job-roles'],
    queryFn: async () => {
      const { data } = await apiClient.get<JobRole[]>('/api/admin/job-roles/');
      return data;
    },
  });
};

// 2. إنشاء دور جديد
export const useCreateJobRole = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (title: string) => {
      const { data } = await apiClient.post('/api/admin/job-roles/', { title });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-job-roles'] });
      toast.success('تمت إضافة الدور الوظيفي بنجاح');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل إضافة الدور');
    }
  });
};

// 3. تحديث دور (Update)
export const useUpdateJobRole = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, title }: { id: number; title: string }) => {
      const { data } = await apiClient.put(`/api/admin/job-roles/${id}`, { title });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-job-roles'] });
      toast.success('تم تحديث الدور الوظيفي بنجاح');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل تحديث الدور');
    }
  });
};

// 4. حذف دور
export const useDeleteJobRole = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/admin/job-roles/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-job-roles'] });
      toast.success('تم حذف الدور الوظيفي');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل الحذف');
    }
  });
};