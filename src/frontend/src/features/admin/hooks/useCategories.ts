import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { toast } from 'sonner';

export interface Category {
  id: number;
  name: string;
}

// 1. جلب التصنيفات
export const useCategories = () => {
  return useQuery({
    queryKey: ['admin-categories'],
    queryFn: async () => {
      const { data } = await apiClient.get<Category[]>('/api/admin/categories');
      return data;
    },
  });
};

// 2. إنشاء تصنيف
export const useCreateCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (name: string) => {
      const { data } = await apiClient.post('/api/admin/categories', { name });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-categories'] });
      toast.success('تمت إضافة التصنيف بنجاح');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل إضافة التصنيف');
    }
  });
};

// 3. تحديث تصنيف (Update)
export const useUpdateCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, name }: { id: number; name: string }) => {
      const { data } = await apiClient.put(`/api/admin/categories/${id}`, { name });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-categories'] });
      toast.success('تم تحديث التصنيف بنجاح');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'فشل تحديث التصنيف');
    }
  });
};

// 4. حذف تصنيف
export const useDeleteCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/admin/categories/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-categories'] });
      toast.success('تم حذف التصنيف');
    },
    onError: (err: any) => {
        toast.error(err.response?.data?.detail || 'لا يمكن حذف هذا التصنيف');
    }
  });
};