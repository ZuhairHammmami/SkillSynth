import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';

export interface Resource {
  id: number;
  title: string;
  url: string;
  type: string;
  is_free: boolean;
  author_or_platform?: string;
}

export interface ResourceData {
  title: string;
  url: string;
  type: string;
  is_free: boolean;
  author_or_platform?: string;
}

// 1. جلب المصادر
export const useResources = () => {
  return useQuery({
    queryKey: ['admin-resources'],
    queryFn: async () => {
      const { data } = await apiClient.get<Resource[]>('/api/admin/resources/');
      return data;
    },
  });
};

// 2. إنشاء مصدر
export const useCreateResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: ResourceData) => {
      const response = await apiClient.post('/api/admin/resources/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-resources'] });
      toast.success('تمت إضافة المصدر بنجاح');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل إضافة المصدر');
    }
  });
};

// 3. تحديث مصدر (الجديد)
export const useUpdateResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: ResourceData }) => {
      const response = await apiClient.put(`/api/admin/resources/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-resources'] });
      toast.success('تم تحديث المصدر بنجاح');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل تحديث المصدر');
    }
  });
};

// 4. حذف مصدر
export const useDeleteResource = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/admin/resources/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-resources'] });
      toast.success('تم حذف المصدر');
    },
    onError: (err: any) => {
        toast.error('فشل حذف المصدر');
    }
  });
};