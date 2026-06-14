'use client';
import { useEffect, useState } from 'react';
import apiClient from '@/shared/lib/api';
import { Button } from '@/shared/ui/button';
import { Label } from '@/shared/ui/label';
import { AssessmentAnswer } from '@/app/wizard/page';
import { Skeleton } from '@/shared/ui/skeleton';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, ChevronRight, ChevronLeft } from 'lucide-react';

interface Question {
  id: string;
  skill: string;
  text: string;
  options: string[];
}
interface Props {
  jobRole: string;
  onComplete: (answers: AssessmentAnswer) => void;
}

export default function Step2_Assessment({ jobRole, onComplete }: Props) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<AssessmentAnswer>({});
  const [isLoading, setIsLoading] = useState(true);
  
  // حالة للتحكم في السؤال الحالي المعروض
  const [currentQIndex, setCurrentQIndex] = useState(0);

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobRole) return;
    setIsLoading(true);
    setError(null);
    apiClient.get<Question[]>(`/api/assessments/${encodeURIComponent(jobRole)}`)
      .then(res => setQuestions(res.data))
      .catch(err => {
        console.error(err);
        setError("تعذر تحميل الأسئلة. يرجى التحقق من اتصالك والمحاولة مرة أخرى.");
      })
      .finally(() => setIsLoading(false));
  }, [jobRole]);
  
  const handleAnswer = (optionIndex: number) => {
    // حفظ الإجابة
    const currentQ = questions[currentQIndex];
    setAnswers(prev => ({ ...prev, [currentQ.id]: optionIndex }));

    // الانتقال للسؤال التالي تلقائياً بعد تأخير بسيط
    if (currentQIndex < questions.length - 1) {
        setTimeout(() => setCurrentQIndex(prev => prev + 1), 250);
    }
  };

  const handleFinish = () => {
      onComplete(answers);
  };

  if (isLoading) return (
      <div className="space-y-4">
          <Skeleton className="h-8 w-3/4 mx-auto" />
          <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
          </div>
      </div>
  );

  if (error) return (
    <div className="text-center space-y-4 py-8">
      <div className="text-4xl">🔌</div>
      <h3 className="text-xl font-bold text-destructive">تعذر الاتصال</h3>
      <p className="text-muted-foreground">{error}</p>
      <Button onClick={() => window.location.reload()} variant="outline">
        إعادة المحاولة
      </Button>
    </div>
  );

  if (questions.length === 0) return (
    <div className="text-center space-y-4 py-8">
      <h3 className="text-xl font-bold">لا توجد أسئلة متاحة</h3>
      <p className="text-muted-foreground">لم نجد أسئلة تقييم لهذا الدور الوظيفي. يمكنك المتابعة إلى الخطوة التالية.</p>
      <Button onClick={() => onComplete({})} variant="default">
        متابعة بدون تقييم
      </Button>
    </div>
  );

  const currentQ = questions[currentQIndex];
  const progress = ((currentQIndex + 1) / questions.length) * 100;

  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-primary">لنقيّم خبرتك الحالية</h2>
        <p className="text-muted-foreground">أجب بصدق لنتمكن من تحديد نقطة البداية المثالية لك.</p>
        
        {/* شريط تقدم داخلي للأسئلة */}
        <div className="w-full h-2 bg-muted rounded-full mt-4 overflow-hidden">
            <motion.div 
                className="h-full bg-blue-500" 
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
            />
        </div>
        <p className="text-xs text-muted-foreground mt-1 text-right">سؤال {currentQIndex + 1} من {questions.length}</p>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
            key={currentQ.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
        >
            <h3 className="text-xl font-semibold leading-relaxed">{currentQ.text}</h3>
            
            <div className="grid gap-3">
                {currentQ.options.map((option, index) => {
                    const isSelected = answers[currentQ.id] === index;
                    return (
                        <div 
                            key={index}
                            onClick={() => handleAnswer(index)}
                            className={`
                                p-4 rounded-lg border-2 cursor-pointer transition-all flex items-center justify-between group
                                ${isSelected 
                                    ? 'border-primary bg-primary/5 shadow-sm' 
                                    : 'border-muted hover:border-primary/30 hover:bg-muted/20'}
                            `}
                        >
                            <span className="font-medium">{option}</span>
                            {isSelected && (
                                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
                                    <Check className="w-5 h-5 text-primary" />
                                </motion.div>
                            )}
                        </div>
                    );
                })}
            </div>
        </motion.div>
      </AnimatePresence>

      <div className="flex justify-between pt-6 border-t">
        <Button 
            variant="ghost" 
            disabled={currentQIndex === 0}
            onClick={() => setCurrentQIndex(prev => prev - 1)}
        >
            <ChevronRight className="w-4 h-4 ml-2" /> السابق
        </Button>

        {currentQIndex === questions.length - 1 ? (
            <Button onClick={handleFinish} disabled={Object.keys(answers).length !== questions.length}>
                عرض النتيجة <Check className="w-4 h-4 mr-2" />
            </Button>
        ) : (
            <Button 
                variant="outline"
                disabled={answers[currentQ.id] === undefined} 
                onClick={() => setCurrentQIndex(prev => prev + 1)}
            >
                التالي <ChevronLeft className="w-4 h-4 mr-2" />
            </Button>
        )}
      </div>
    </div>
  );
}