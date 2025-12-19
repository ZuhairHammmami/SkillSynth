// المسار: src/app/components/profile/UpdateProfileForm.tsx
'use client';

import { useState } from 'react';
import apiClient from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from "sonner";
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

// تعريف شكل بيانات المستخدم التي يستقبلها المكون
interface User {
  email: string;
  full_name: string;
  id: number;
  is_admin: boolean;
}

// تعريف شكل الخصائص (Props) التي يستقبلها المكون
interface Props {
  user: User;
}

export const UpdateProfileForm = ({ user }: Props) => {
  // استدعاء "الدماغ" للحصول على دالة تحديث بيانات المستخدم
  const { refetchUser } = useAuth();
  
  // حالة محلية لتخزين قيمة حقل "الاسم الكامل"
  const [fullName, setFullName] = useState(user.full_name);
  
  // حالة محلية لتتبع حالة تحميل الطلب
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // منع السلوك الافتراضي للنموذج (إعادة تحميل الصفحة)

    // التحقق مما إذا كان المستخدم قد أجرى أي تغيير
    if (fullName === user.full_name) {
        toast.info("لم تقم بإجراء أي تغييرات على اسمك.");
        return; // أوقف التنفيذ إذا لم يتغير الاسم
    }
    
    setIsLoading(true); // ابدأ حالة التحميل

    try {
      // إرسال طلب PUT إلى الباك اند لتحديث الاسم
      await apiClient.put('/api/users/me', { full_name: fullName });
      
      // عند النجاح، أظهر إشعار نجاح
      toast.success("تم تحديث اسمك بنجاح!");
      
      // قم بتحديث بيانات المستخدم في كامل التطبيق (سيؤدي هذا إلى تحديث الاسم في الهيدر فورًا)
      await refetchUser();

    } catch (error) {
      // في حالة الفشل، أظهر إشعار خطأ
      toast.error("فشل تحديث الملف الشخصي. يرجى المحاولة مرة أخرى.");
    } finally {
      // قم دائمًا بإيقاف حالة التحميل بعد انتهاء الطلب (سواء نجح أم فشل)
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="email">البريد الإلكتروني</Label>
        <Input 
          id="email" 
          type="email" 
          value={user.email} 
          disabled // البريد الإلكتروني غير قابل للتعديل
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
          disabled={isLoading}
        />
      </div>
      <Button type="submit" disabled={isLoading} className="w-full sm:w-auto">
        {/* عرض أيقونة التحميل بجانب النص عند التحميل */}
        {isLoading && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
        {isLoading ? 'جارٍ الحفظ...' : 'حفظ التغييرات'}
      </Button>
    </form>
  );
};