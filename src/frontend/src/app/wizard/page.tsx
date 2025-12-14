// المسار: src/app/wizard/page.tsx
'use client';

import { useState } from 'react';
// سنقوم بإنشاء هذه المكونات في الخطوات التالية
import Step1_SelectGoal from '@/app/components/wizard/Step1_SelectGoal';
import Step2_Assessment from '@/app/components/wizard/Step2_Assessment';
import Step3_Preferences from '@/app/components/wizard/Step3_Preferences';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

// تعريف أنواع البيانات التي سنجمعها عبر الخطوات
export interface AssessmentAnswer {
  [questionId: string]: number;
}
export interface UserPreferences {
  is_free: boolean;
  format: string;
  language: string;
}

export default function WizardPage() {
  const [step, setStep] = useState(1);
  const [jobRole, setJobRole] = useState<string>('');
  const [answers, setAnswers] = useState<AssessmentAnswer>({});

  const handleGoalSelect = (selectedRole: string) => {
    setJobRole(selectedRole);
    setStep(2);
  };

  const handleAssessmentComplete = (assessmentAnswers: AssessmentAnswer) => {
    setAnswers(assessmentAnswers);
    setStep(3);
  };

  return (
    <div className="container mx-auto flex justify-center py-16 px-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl">أنشئ مسارك التعليمي الذكي</CardTitle>
          <CardDescription className="pt-2">
            {step === 1 && "ابدأ باختيار هدفك الوظيفي."}
            {step === 2 && `اختبار تحديد المستوى لـ: ${jobRole}`}
            {step === 3 && "الخطوة الأخيرة: حدد تفضيلاتك."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {step === 1 && <Step1_SelectGoal onGoalSelect={handleGoalSelect} />}
          {step === 2 && <Step2_Assessment jobRole={jobRole} onComplete={handleAssessmentComplete} />}
          {step === 3 && <Step3_Preferences jobRole={jobRole} answers={answers} />}
        </CardContent>
      </Card>
    </div>
  );
}