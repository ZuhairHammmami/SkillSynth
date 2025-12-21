// المسار: src/features/wizard/components/Step3_Preferences.tsx
'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useGeneratePath } from '@/features/wizard/hooks/useGeneratePath';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { AssessmentAnswer, WizardOptions } from '@/app/wizard/page';
import type { FC } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface Props {
  jobRole: string;
  answers: AssessmentAnswer;
  options: WizardOptions | null;
}

const Step3_Preferences: FC<Props> = ({ jobRole, answers, options }) => {
  const router = useRouter();
  const [hours, setHours] = useState(10);
  const [format, setFormat] = useState('any');
  const [language, setLanguage] = useState('en');

  // استدعاء الـ Hook الخاص بتوليد المسار
  const { mutate: performGenerate, isPending } = useGeneratePath();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      goal: jobRole,
      weekly_hours: hours,
      preferences: { is_free: true, format, language },
      answers,
    };
    
    // استدعاء دالة mutate مع تمرير البيانات ودوال onSuccess/onError
    performGenerate(payload, {
      onSuccess: (data) => {
        if (data && data.id) {
          router.push(`/paths/${data.id}`);
        } else {
          toast.warning("تم توليد المسار، لكن حدث خطأ أثناء التوجيه.");
          router.push('/dashboard');
        }
      },
      onError: (error: any) => {
        // الـ Hook سيعرض رسالة الخطأ العامة، لكن يمكننا إضافة منطق مخصص هنا إذا أردنا
        console.error("Generate path failed in component:", error);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="hours">كم ساعة يمكنك تخصيصها أسبوعيًا؟</Label>
        <Input 
          id="hours" 
          type="number" 
          value={hours} 
          onChange={(e) => setHours(parseInt(e.target.value) || 0)} 
          required 
          disabled={isPending}
        />
      </div>

      <div className="space-y-2">
        <Label>تنسيق المحتوى المفضل؟</Label>
        <Select onValueChange={setFormat} defaultValue={format} disabled={isPending}>
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
        <Select onValueChange={setLanguage} defaultValue={language} disabled={isPending}>
          <SelectTrigger>
            <SelectValue placeholder="اختر لغة..." />
          </SelectTrigger>
          <SelectContent>
            {options?.preferences.languages.map((l: string) => <SelectItem key={l} value={l}>{l === 'en' ? 'English' : 'العربية'}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      <Button type="submit" className="w-full" disabled={isPending}>
        {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
        {isPending ? '⏳ جارٍ تحليل إجاباتك...' : '🚀 ولّد المسار الذكي'}
      </Button>
    </form>
  );
};

export default Step3_Preferences;