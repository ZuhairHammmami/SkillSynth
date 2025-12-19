// المسار: src/app/components/wizard/Step3_Preferences.tsx
'use client';
import { useState } from 'react';
import apiClient from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { AssessmentAnswer, WizardOptions } from '@/app/wizard/page';
import type { FC } from 'react';

interface Props {
  jobRole: string;
  answers: AssessmentAnswer;
  options: WizardOptions | null; // <-- استقبال الخيارات
}

const Step3_Preferences: FC<Props> = ({ jobRole, answers, options }) => {
  const router = useRouter();
  const [hours, setHours] = useState(10);
  const [format, setFormat] = useState('any');
  const [language, setLanguage] = useState('en');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    const payload = {
      goal: jobRole,
      weekly_hours: hours,
      preferences: { is_free: true, format, language },
      answers,
    };

    try {
      const response = await apiClient.post('/api/generate-path/', payload);
      if (response.data && response.data.id) {
          router.push(`/paths/${response.data.id}`);
      } else {
          console.warn("API did not return a path ID. Redirecting to dashboard.");
          router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An internal server error occurred');
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
        <Label>تنسيق المحتوى المفضل؟</Label>
        <Select onValueChange={setFormat} defaultValue={format}>
          <SelectTrigger>
            <SelectValue placeholder="اختر تنسيقًا..." />
          </SelectTrigger>
          <SelectContent>
            {options?.preferences.formats.map((f: string) => <SelectItem key={f} value={f}>{f}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      
      <div className="space-y-2">
        <Label>لغة المحتوى المفضلة؟</Label>
        <Select onValueChange={setLanguage} defaultValue={language}>
          <SelectTrigger>
            <SelectValue placeholder="اختر لغة..." />
          </SelectTrigger>
          <SelectContent>
            {options?.preferences.languages.map((l: string) => <SelectItem key={l} value={l}>{l === 'en' ? 'English' : 'العربية'}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {error && <p className="text-sm font-medium text-destructive">{error}</p>}
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? '⏳ جارٍ تحليل إجاباتك...' : '🚀 ولّد المسار الذكي'}
      </Button>
    </form>
  );
};

export default Step3_Preferences;