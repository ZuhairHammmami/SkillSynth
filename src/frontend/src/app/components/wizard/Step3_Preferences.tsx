// المسار: src/app/components/wizard/Step3_Preferences.tsx
'use client';
import { useState } from 'react';
import apiClient from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AssessmentAnswer } from '@/app/wizard/page';

interface Props {
  jobRole: string;
  answers: AssessmentAnswer;
}

export default function Step3_Preferences({ jobRole, answers }: Props) {
  const router = useRouter();
  const [hours, setHours] = useState(10);
  const [format, setFormat] = useState('any'); // video, article, etc.
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    const payload = {
      goal: jobRole,
      weekly_hours: hours,
      preferences: {
        is_free: true, // يمكن أن يصبح خيارًا للمستخدم لاحقًا
        format: format,
        language: 'en', // يمكن أن يصبح خيارًا للمستخدم لاحقًا
      },
      answers: answers,
    };

    try {
      const response = await apiClient.post('/api/generate-path/', payload);
      // افترض أن الاستجابة تحتوي على ID المسار
      router.push(`/paths/${response.data.id}`); 
    } catch (err: any) {
      setError(err.response?.data?.detail || 'حدث خطأ أثناء إنشاء المسار.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="hours">كم ساعة يمكنك تخصيصها أسبوعيًا؟</Label>
        <Input id="hours" type="number" value={hours} onChange={(e) => setHours(parseInt(e.target.value) || 0)} required />
      </div>
      <div className="space-y-2">
        <Label htmlFor="format">تنسيق المحتوى المفضل؟</Label>
        <Input id="format" value={format} onChange={(e) => setFormat(e.target.value)} />
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? '⏳ جارٍ تحليل إجاباتك...' : '🚀 ولّد المسار الذكي'}
      </Button>
    </form>
  );
}