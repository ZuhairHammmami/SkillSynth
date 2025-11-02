// المسار: src/frontend/src/app/components/GenerateWizard.tsx
'use client';

import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/context/AuthContext'; // <-- 1. استيراد خطاف المصادقة

// ... الواجهات تبقى كما هي

export default function GenerateWizard() {
  const router = useRouter();
  const { token, isAuthenticated } = useAuth(); // <-- 2. الحصول على التوكن وحالة المصادقة
  // ... بقية الـ states تبقى كما هي
  const [goal, setGoal] = useState('frontend_developer');
  const [hours, setHours] = useState(10);
  const [preferences, setPreferences] = useState('video,article');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // <-- 3. التحقق من تسجيل الدخول قبل إرسال الطلب
    if (!isAuthenticated) {
      setError('يجب عليك تسجيل الدخول أولاً لتوليد مسار.');
      // يمكنك أيضًا توجيه المستخدم إلى صفحة تسجيل الدخول
      // router.push('/login');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    const payload = { goal, weekly_hours: hours, preferences: { format: preferences } };

    try {
      // <-- 4. إضافة هيدر المصادقة إلى الطلب
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/generate-path/`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`, // هذا هو "المفتاح"
          },
        }
      );
      // ... لاحقًا، سنقوم بتوجيه المستخدم إلى صفحة المسار
      console.log('Path Generated:', response.data);

    } catch (err: any) {
      console.error('API Error:', err);
      setError(err.response?.data?.detail || 'حدث خطأ أثناء إنشاء المسار.');
    } finally {
      setIsLoading(false);
    }
  };

  // ... قسم ה-return يبقى كما هو
  return (
    <form
      onSubmit={handleSubmit}
      className="p-8 bg-card text-card-foreground rounded-lg border shadow-lg space-y-6 w-full max-w-md mx-auto"
    >
        {/* ... */}
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? '⏳ جارٍ التوليد...' : '🚀 ولّد المسار'}
        </Button>
    </form>
  );
}