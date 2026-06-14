// المسار: src/features/user/components/UpdateProfileForm.tsx
'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Label } from '@/shared/ui/label';
import { toast } from "sonner";
import { Loader2 } from 'lucide-react';
import type { User } from '@/shared/store/authStore'; // <-- استيراد نوع User من المخزن المركزي

interface Props {
  user: User;
}

// 1. تعريف دالة التحديث خارج المكون
const updateUser = async (updatedData: { full_name: string }) => {
  const { data } = await apiClient.put<User>('/api/auth/users/me', updatedData);
  return data;
};

export const UpdateProfileForm = ({ user }: Props) => {
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState(user.full_name);

  // 2. استخدام useMutation من React Query لإدارة الطلب
  const { mutate: performUpdate, isPending } = useMutation({
    mutationFn: updateUser,
    onSuccess: (updatedUser) => {
      // عند النجاح، قم بتحديث بيانات 'user' في ذاكرة React Query
      queryClient.setQueryData(['user'], updatedUser);
      toast.success("تم تحديث اسمك بنجاح!");
    },
    onError: () => {
      toast.error("فشل تحديث الملف الشخصي. يرجى المحاولة مرة أخرى.");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (fullName === user.full_name) {
      toast.info("لم تقم بإجراء أي تغييرات على اسمك.");
      return;
    }
    performUpdate({ full_name: fullName });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="email">البريد الإلكتروني</Label>
        <Input 
          id="email" 
          type="email" 
          value={user.email} 
          disabled 
          className="opacity-75 cursor-not-allowed"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="fullName">الاسم الكامل</Label>
        <Input 
          id="fullName" 
          value={fullName} 
          onChange={(e) => setFullName(e.target.value)} 
          required 
          disabled={isPending}
        />
      </div>
      <Button type="submit" disabled={isPending} className="w-full sm:w-auto">
        {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
        {isPending ? 'جارٍ الحفظ...' : 'حفظ التغييرات'}
      </Button>
    </form>
  );
};