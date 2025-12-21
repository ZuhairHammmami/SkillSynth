'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';
import Step1_SelectGoal from '@/features/wizard/components/Step1_SelectGoal';
import Step2_Assessment from '@/features/wizard/components/Step2_Assessment';
import Step3_Preferences from '@/features/wizard/components/Step3_Preferences';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import { motion, AnimatePresence } from 'framer-motion';

// تعريفات الأنواع
export interface AssessmentAnswer { [questionId: string]: number; }
export interface WizardOptions {
  job_roles: string[];
  preferences: {
    formats: string[];
    languages: string[];
  }
}

function WizardContent() {
  const [step, setStep] = useState(1);
  const [options, setOptions] = useState<WizardOptions | null>(null);
  const [jobRole, setJobRole] = useState<string>('');
  const [answers, setAnswers] = useState<AssessmentAnswer>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await apiClient.get<WizardOptions>('/api/wizard-options');
        setOptions(response.data);
      } catch (err) {
        console.error("Failed options", err);
        setError("فشل الاتصال بالمعالج الذكي. يرجى التأكد من اتصالك.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchOptions();
  }, []);

  const handleGoalSelect = (selectedRole: string) => {
    setJobRole(selectedRole);
    setStep(2);
  };

  const handleAssessmentComplete = (assessmentAnswers: AssessmentAnswer) => {
    setAnswers(assessmentAnswers);
    setStep(3);
  };

  const stepsInfo = [
    { id: 1, title: "الهدف", icon: "🎯" },
    { id: 2, title: "المستوى", icon: "📊" },
    { id: 3, title: "التفضيلات", icon: "⚙️" },
  ];

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center space-y-4 py-20">
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-64 w-full max-w-2xl rounded-xl" />
    </div>
  );

  if (error) return (
    <Alert variant="destructive" className="max-w-2xl mx-auto mt-10">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>عذراً</AlertTitle>
      <AlertDescription>{error}</AlertDescription>
    </Alert>
  );

  return (
    <div className="w-full max-w-3xl mx-auto space-y-8">
      {/* مؤشر التقدم العلوي */}
      <div className="relative flex justify-between items-center px-10">
        {/* الخط الخلفي */}
        <div className="absolute top-1/2 left-0 w-full h-1 bg-muted -z-10 rounded-full" />
        {/* الخط الملون المتحرك */}
        <motion.div 
            className="absolute top-1/2 right-0 h-1 bg-primary rounded-full -z-10"
            initial={{ width: "0%" }}
            animate={{ width: `${((step - 1) / (stepsInfo.length - 1)) * 100}%` }}
            transition={{ duration: 0.5 }}
        />

        {stepsInfo.map((s) => {
            const isCompleted = step > s.id;
            const isCurrent = step === s.id;
            
            return (
                <div key={s.id} className="flex flex-col items-center gap-2 bg-background p-2 rounded-lg">
                    <motion.div 
                        className={`
                            w-10 h-10 rounded-full flex items-center justify-center border-2 text-lg font-bold transition-colors
                            ${isCompleted ? 'bg-green-500 border-green-500 text-white' : 
                              isCurrent ? 'bg-primary border-primary text-primary-foreground' : 
                              'bg-background border-muted text-muted-foreground'}
                        `}
                        animate={isCurrent ? { scale: 1.1 } : { scale: 1 }}
                    >
                        {isCompleted ? <CheckCircle2 className="w-6 h-6" /> : s.id}
                    </motion.div>
                    <span className={`text-xs font-medium ${isCurrent ? 'text-primary' : 'text-muted-foreground'}`}>
                        {s.title}
                    </span>
                </div>
            );
        })}
      </div>

      {/* المحتوى الرئيسي مع تأثيرات الحركة */}
      <AnimatePresence mode="wait">
        <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
        >
            <Card className="p-6 sm:p-10 shadow-lg border-primary/10 relative overflow-hidden">
                {/* تأثير خلفية خفيفة */}
                <div className="absolute -top-20 -left-20 w-40 h-40 bg-primary/5 rounded-full blur-3xl" />
                <div className="absolute -bottom-20 -right-20 w-40 h-40 bg-blue-500/5 rounded-full blur-3xl" />
                
                {options && (
                    <>
                        {step === 1 && <Step1_SelectGoal options={options} onGoalSelect={handleGoalSelect} />}
                        {step === 2 && <Step2_Assessment jobRole={jobRole} onComplete={handleAssessmentComplete} />}
                        {step === 3 && <Step3_Preferences jobRole={jobRole} answers={answers} options={options} />}
                    </>
                )}
            </Card>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export default function WizardPage() {
    return (
        <AuthGuard>
            <div className="container mx-auto py-16 px-4">
                <WizardContent />
            </div>
        </AuthGuard>
    )
}