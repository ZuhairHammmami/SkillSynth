// المسار: src/frontend/src/app/components/GenerateWizard.tsx
'use client';

import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/context/AuthContext';

// تعريف أنواع البيانات للطلب والاستجابة
interface GeneratePathPayload {
  goal: string;
  weekly_hours: number;
  preferences: { [key: string]: any };
}
interface GeneratePathResponse {
  id: number; // نتوقع أن يعيد الباك اند معرّف المسار الجديد
  // ... أي بيانات أخرى قد تأتي من الاستجابة
}

export default function GenerateWizard() {
  const router = useRouter();
  const { token, isAuthenticated } = useAuth();

  // States لحقول النموذج
  const [goal, setGoal] = useState('frontend_developer');
  const [hours, setHours] = useState(10);
  const [preferences, setPreferences] = useState('video,article');
  
  // States لحالة الطلب
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // التحقق من تسجيل الدخول قبل إرسال الطلب
    if (!isAuthenticated) {
      setError('يجب عليك تسجيل الدخول أولاً لتوليد مسار.');
      return;
    }
    
    setIsLoading(true);
    setError(null);

    // تجهيز البيانات التي سيتم إرسالها للباك اند
    const payload: GeneratePathPayload = {
      goal,
      weekly_hours: hours,
      preferences: {
        // سنقوم بمعالجة النص لتحويله إلى مصفوفة نظيفة
        tags: preferences
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag),
      },
    };

    try {
      const response = await axios.post<GeneratePathResponse>(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/generate-path/`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`, // إضافة هيدر المصادقة
          },
        }
      );

      // ----- هذه هي الإضافة الحاسمة -----
      // عند النجاح، احصل على ID المسار الجديد ووجه المستخدم إليه
      const newPathId = response.data.id;
      router.push(`/paths/${newPathId}`);
      // ------------------------------------

    } catch (err: any) {
      console.error('API Error:', err);
      setError(err.response?.data?.detail || 'حدث خطأ أثناء إنشاء المسار. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-8 bg-card text-card-foreground rounded-lg border shadow-lg space-y-6 w-full max-w-md mx-auto"
    >
      {/* ===== هذا هو قسم حقول النموذج الكامل ===== */}
      <div className="grid w-full items-center gap-1.5">
        <Label htmlFor="goal">ما هو هدفك التعليمي؟</Label>
        <Input
          id="goal"
          placeholder="مثال: frontend_developer"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          required
          disabled={isLoading}
        />
      </div>

      <div className="grid w-full items-center gap-1.5">
        <Label htmlFor="hours">كم ساعة يمكنك تخصيصها أسبوعيًا؟</Label>
        <Input
          id="hours"
          type="number"
          value={hours}
          onChange={(e) => setHours(parseInt(e.target.value) || 0)}
          required
          disabled={isLoading}
          min={1}
        />
      </div>

      <div className="grid w-full items-center gap-1.5">
        <Label htmlFor="preferences">ما هي تفضيلاتك؟ (فيديو، مقالات...)</Label>
        <Input
          id="preferences"
          placeholder="افصل بينها بفاصلة: video,article"
          value={preferences}
          onChange={(e) => setPreferences(e.target.value)}
          disabled={isLoading}
        />
      </div>

      {error && (
        <p className="text-sm font-medium text-destructive bg-destructive/10 p-2 rounded">
          {error}
        </p>
      )}

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? '⏳ جارٍ التوليد...' : '🚀 ولّد المسار'}
      </Button>
      {/* ========================================= */}
    </form>
  );
}