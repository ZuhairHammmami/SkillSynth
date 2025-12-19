// المسار: src/app/paths/[id]/page.tsx
'use client';
import { useEffect, useState } from 'react';
import { notFound, useParams } from 'next/navigation';
import apiClient from '@/lib/api';
import StepItem from '@/app/components/StepItem';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Terminal } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

// ... تعريف أنواع البيانات يبقى كما هو، مع إضافة id للخطوة
interface StepResource { url: string; title: string; }
interface PathStep {
  id: number; // <-- إضافة مهمة من الباك اند
  step_number: number;
  title: string;
  content: string;
}
interface PathDetails { /* ... */ steps: PathStep[]; }

export default function PathDetailPage() {
  const params = useParams();
  const pathId = params.id as string;
  const { isAuthenticated } = useAuth();
  const [pathDetails, setPathDetails] = useState<PathDetails | null>(null);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set()); // <-- 1. State جديد لتتبع التقدم
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // ... (منطق جلب البيانات يبقى كما هو)
    if (isAuthenticated && pathId) {
        // ...
    }
  }, [pathId, isAuthenticated]);
  
  // 2. دالة جديدة لمعالجة إكمال الخطوة
  const handleCompleteStep = async (stepId: number) => {
    // لا تسمح بإكمال نفس الخطوة مرتين
    if (completedSteps.has(stepId)) return;
    try {
      await apiClient.post(`/api/steps/${stepId}/complete`);
      // عند النجاح، قم بتحديث الحالة المحلية فورًا
      setCompletedSteps(prev => new Set(prev).add(stepId));
    } catch (err) {
      console.error("Failed to mark step as complete", err);
      // يمكنك هنا إظهار إشعار خطأ للمستخدم
    }
  };

  if (isLoading) return <div className="text-center p-10">⏳ جارٍ التحميل...</div>;
  if (error || !pathDetails) return notFound();

  return (
    <main className="container mx-auto max-w-4xl p-4 sm:p-8">
      {/* ... (JSX الخاص بعنوان الصفحة يبقى كما هو) */}
      <div className="space-y-6">
        {pathDetails.steps.map((step) => {
          let resource: StepResource | null = null;
          try {
              if(step.content) resource = JSON.parse(step.content);
          } catch (e) { console.error("Failed to parse content", e); }
          
          return (
            <StepItem
              key={step.id} // <-- استخدام id الفريد كمفتاح
              stepId={step.id} // <-- تمرير id الخطوة
              stepNumber={step.step_number}
              title={step.title}
              resourceTitle={resource?.title || 'المورد غير متوفر'}
              resourceUrl={resource?.url || '#'}
              isCompleted={completedSteps.has(step.id)} // <-- تمرير حالة الإكمال
              onComplete={handleCompleteStep} // <-- تمرير دالة المعالجة
            />
          );
        })}
      </div>
      {/* ... (JSX الخاص بالمسار الفارغ يبقى كما هو) */}
    </main>
  );
}