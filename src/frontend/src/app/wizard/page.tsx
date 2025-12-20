// المسار: src/app/wizard/page.tsx
'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';
import Step1_SelectGoal from '@/features/wizard/components/Step1_SelectGoal';
import Step2_Assessment from '@/features/wizard/components/Step2_Assessment';
import Step3_Preferences from '@/features/wizard/components/Step3_Preferences';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { AuthGuard } from '@/features/auth/components/AuthGuard';

// تعريف أنواع البيانات التي سنستخدمها
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
        console.error("Failed to load wizard options", err);
        setError("فشل في تحميل إعدادات المعالج. يرجى المحاولة مرة أخرى.");
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

  const renderStepContent = () => {
    if (isLoading) {
      return <Skeleton className="h-48 w-full" />;
    }
    if (error) {
      return (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>حدث خطأ</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      );
    }
    if (!options) return null;

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
  };

  return (
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
        {renderStepContent()}
      </CardContent>
    </Card>
  );
}

export default function WizardPage() {
    return (
        <AuthGuard>
            <div className="container mx-auto flex justify-center py-16 px-4">
                <WizardContent />
            </div>
        </AuthGuard>
    )
}