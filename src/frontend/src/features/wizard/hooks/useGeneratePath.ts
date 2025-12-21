// المسار: src/features/wizard/hooks/useGeneratePath.ts
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';

// تعريف شكل البيانات التي نرسلها ونتلقاها
interface GeneratePathPayload { /* ... goal, weekly_hours, etc. */ }
interface GeneratePathResponse { id: number; }

const generatePath = async (payload: GeneratePathPayload): Promise<GeneratePathResponse> => {
  const { data } = await apiClient.post<GeneratePathResponse>('/api/generate-path/', payload);
  return data;
};

export const useGeneratePath = () => {
  return useMutation({
    mutationFn: generatePath,
    onSuccess: () => {
      toast.success("تم توليد مسارك بنجاح!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'حدث خطأ أثناء إنشاء المسار.');
    },
  });
};