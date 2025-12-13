'use client';
import { useState } from 'react';
import apiClient from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface GeneratePathResponse { id: number; }

export default function GenerateWizard() {
  const router = useRouter();
  const [goal, setGoal] = useState('frontend_developer');
  const [hours, setHours] = useState(10);
  const [preferences, setPreferences] = useState('video,article');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const payload = {
      goal,
      weekly_hours: hours,
      preferences: { tags: preferences.split(',').map(tag => tag.trim()).filter(Boolean) },
    };

    try {
      // apiClient سيضيف التوكن تلقائيًا من الكوكيز
      const response = await apiClient.post<GeneratePathResponse>('/api/generate-path/', payload);
      router.push(`/paths/${response.data.id}`);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('جلسة الدخول غير صالحة. يرجى تسجيل الخروج ثم الدخول مرة أخرى.');
      } else {
        setError(err.response?.data?.detail || 'حدث خطأ أثناء إنشاء المسار.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="goal">ما هو هدفك التعليمي؟</Label>
        <Input id="goal" value={goal} onChange={(e) => setGoal(e.target.value)} required disabled={isLoading} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="hours">كم ساعة يمكنك تخصيصها أسبوعيًا؟</Label>
        <Input id="hours" type="number" value={hours} onChange={(e) => setHours(parseInt(e.target.value) || 0)} required disabled={isLoading} min={1} />
      </div>
      <div className="space-y-2">
        <Label htmlFor="preferences">ما هي تفضيلاتك؟</Label>
        <Input id="preferences" value={preferences} onChange={(e) => setPreferences(e.target.value)} disabled={isLoading} />
      </div>
      {error && <p className="text-sm font-medium text-destructive">{error}</p>}
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? '⏳ جارٍ التوليد...' : '🚀 ولّد المسار'}
      </Button>
    </form>
  );
}