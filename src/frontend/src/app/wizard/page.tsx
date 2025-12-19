// المسار: src/app/wizard/page.tsx
'use client';
import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';
import Step1_SelectGoal from '@/app/components/wizard/Step1_SelectGoal';
import Step2_Assessment from '@/app/components/wizard/Step2_Assessment';
import Step3_Preferences from '@/app/components/wizard/Step3_Preferences';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

// تعريف أنواع البيانات التي سنستخدمها عبر المكونات
export interface AssessmentAnswer { [questionId: string]: number; }
export interface WizardOptions {
  job_roles: string[];
  preferences: {
    formats: string[];
    languages: string[];
  }
}

export default function WizardPage() {
  const [step, setStep] = useState(1);
  const [options, setOptions] = useState<WizardOptions | null>(null);
  const [jobRole, setJobRole] = useState<string>('');
  const [answers, setAnswers] = useState<AssessmentAnswer>({});
  const [isLoadingOptions, setIsLoadingOptions] = useState(true);

  // جلب الخيارات مرة واحدة فقط عند تحميل المكون
  useEffect(() => {
    apiClient.get<WizardOptions>('/api/wizard-options')
      .then(res => setOptions(res.data))
      .catch(err => console.error("Failed to load wizard options", err))
      .finally(() => setIsLoadingOptions(false));
  }, []);

  const handleGoalSelect = (selectedRole: string) => {
    setJobRole(selectedRole);
    setStep(2);
  };

  const handleAssessmentComplete = (assessmentAnswers: AssessmentAnswer) => {
    setAnswers(assessmentAnswers);
    setStep(3);
  };

  const renderContent = () => {
    if (isLoadingOptions) {
      return <div className="text-center">⏳ جارٍ تحميل الإعدادات...</div>;
    }
    if (!options) {
      return <div className="text-center text-destructive">فشل في تحميل الإعدادات. يرجى تحديث الصفحة.</div>;
    }
    
    switch (step) {
      case 1:
        return <Step1_SelectGoal options={options} onGoalSelect={handleGoalSelect} />;
      case 2:
        return <Step2_Assessment jobRole={jobRole} onComplete={handleAssessmentComplete} />;
      case 3:
        return <Step3_Preferences jobRole={jobRole} answers={answers} options={options} />;
      default:
        return null;
    }
  }

  return (
    <div className="container mx-auto flex justify-center py-16 px-4">
      <Card className="w-full max-w-2xl transition-all">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl">أنشئ مسارك التعليمي الذكي</CardTitle>
          <CardDescription className="pt-2">
            {step === 1 && "الخطوة 1 من 3: اختر هدفك الرئيسي"}
            {step === 2 && `الخطوة 2 من 3: اختبار تحديد المستوى لـ: ${jobRole}`}
            {step === 3 && "الخطوة 3 من 3: اللمسات الأخيرة"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {renderContent()}
        </CardContent>
      </Card>
    </div>
  );
}