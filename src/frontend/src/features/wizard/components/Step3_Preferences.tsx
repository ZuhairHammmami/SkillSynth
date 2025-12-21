'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useGeneratePath } from '@/features/wizard/hooks/useGeneratePath';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider'; 
import { Loader2, Clock, BookOpen, Video, FileText, Globe, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import type { AssessmentAnswer, WizardOptions } from '@/app/wizard/page';

interface Props {
  jobRole: string;
  answers: AssessmentAnswer;
  options: WizardOptions | null;
}

export default function Step3_Preferences({ jobRole, answers, options }: Props) {
  const router = useRouter();
  
  // القيم الافتراضية تضمن عدم وجود حقول فارغة
  const [hours, setHours] = useState([10]); // Slider يستخدم مصفوفة دائماً
  const [format, setFormat] = useState('any');
  const [language, setLanguage] = useState('en');

  const { mutate: performGenerate, isPending } = useGeneratePath();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // تجهيز البيانات بنفس الشكل الذي يتوقعه Pydantic Model في الباك اند
    const payload = {
      goal: jobRole,
      weekly_hours: hours[0], // نأخذ القيمة الأولى من المصفوفة
      preferences: { 
          is_free: true, // افتراضي
          format: format, 
          language: language 
      },
      answers: answers,
    };
    
    performGenerate(payload, {
      onSuccess: (data) => {
        if (data && data.id) {
          router.push(`/paths/${data.id}`);
        } else {
          toast.warning("تم إنشاء المسار، جاري تحويلك...");
          router.push('/dashboard');
        }
      }
    });
  };

  // أيقونات لتجميل العرض
  const formatIcons: any = {
      'Video': <Video className="w-6 h-6 mb-2 text-blue-500" />,
      'Article': <FileText className="w-6 h-6 mb-2 text-orange-500" />,
      'Book': <BookOpen className="w-6 h-6 mb-2 text-green-500" />,
      'Course': <BookOpen className="w-6 h-6 mb-2 text-purple-500" />,
      'any': <Sparkles className="w-6 h-6 mb-2 text-yellow-500" />
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 text-center animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-primary">اللمسات الأخيرة ✨</h2>
        <p className="text-muted-foreground">صمم تجربتك التعليمية لتناسب وقتك وأسلوبك.</p>
      </div>

      {/* 1. اختيار ساعات الدراسة (Slider يمنع الخطأ في الأرقام) */}
      <div className="bg-card border border-border/50 p-6 rounded-xl shadow-sm">
        <div className="flex justify-between items-end mb-6">
            <Label className="flex items-center gap-2 text-lg">
                <Clock className="w-5 h-5 text-primary" /> 
                كم ساعة ستدرس أسبوعياً؟
            </Label>
            <span className="text-3xl font-bold text-primary tabular-nums">
                {hours[0]} 
                <span className="text-sm font-medium text-muted-foreground mr-1">ساعة</span>
            </span>
        </div>
        
        <Slider 
            defaultValue={[10]} 
            max={40} 
            min={2} 
            step={1} 
            value={hours} 
            onValueChange={setHours}
            className="py-2 cursor-pointer"
        />
        
        <div className="flex justify-between text-xs text-muted-foreground mt-2 px-1">
            <span>ساعتين (استرخاء ☕)</span>
            <span>40 ساعة (تفرغ كامل 🔥)</span>
        </div>
      </div>

      {/* 2. تنسيق المحتوى (اختيار من متعدد يمنع الخطأ) */}
      <div className="space-y-4">
        <Label className="text-lg font-semibold flex gap-2 justify-center sm:justify-start">
            ما هو أسلوبك المفضل في التعلم؟
        </Label>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {options?.preferences.formats.map((f) => (
                <div 
                    key={f}
                    onClick={() => setFormat(f)}
                    className={`
                        cursor-pointer flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all duration-200
                        ${format === f 
                            ? 'border-primary bg-primary/10 shadow-md scale-105' 
                            : 'border-border hover:border-primary/50 hover:bg-muted/50'}
                    `}
                >
                    {formatIcons[f] || formatIcons['any']}
                    <span className="font-medium text-sm capitalize">
                        {f === 'any' ? 'كوكتيل (مختلط)' : f}
                    </span>
                </div>
            ))}
        </div>
      </div>
      
      {/* 3. اللغة (اختيار من متعدد) */}
      <div className="space-y-4">
        <Label className="text-lg font-semibold flex items-center gap-2 justify-center sm:justify-start">
            <Globe className="w-5 h-5 text-primary" /> 
            لغة المحتوى
        </Label>
        <div className="flex gap-4 justify-center sm:justify-start">
            {options?.preferences.languages.map((l) => (
                <div 
                    key={l}
                    onClick={() => setLanguage(l)}
                    className={`
                        cursor-pointer px-6 py-3 rounded-full border-2 transition-all font-medium min-w-[120px] text-center
                        ${language === l 
                            ? 'border-primary bg-primary text-primary-foreground shadow-md' 
                            : 'border-border hover:border-primary/50 hover:bg-muted/50'}
                    `}
                >
                    {l === 'en' ? 'English' : 'العربية'}
                </div>
            ))}
        </div>
      </div>

      <div className="pt-8">
        <Button 
            type="submit" 
            size="lg" 
            className="w-full text-lg h-14 shadow-xl shadow-primary/20 hover:shadow-primary/40 transition-all hover:-translate-y-1 rounded-xl" 
            disabled={isPending}
        >
            {isPending ? (
                <span className="flex items-center gap-2">
                    <Loader2 className="ml-2 h-6 w-6 animate-spin" />
                    جارٍ استشارة الذكاء الاصطناعي...
                </span>
            ) : (
                '🚀 توليد المسار الآن'
            )}
        </Button>
        <p className="text-xs text-muted-foreground mt-4">
            سيقوم الذكاء الاصطناعي بتحليل إجاباتك وبناء خطة مخصصة لك في ثوانٍ.
        </p>
      </div>
    </form>
  );
}