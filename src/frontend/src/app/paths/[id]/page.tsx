// المسار: src/app/paths/[id]/page.tsx
'use client';

import { useParams, notFound } from 'next/navigation';
import { usePathDetails, PathDetails } from '@/features/paths/hooks/usePathDetails';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import StepItem from '@/components/StepItem'; // <-- تم نقله
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Terminal } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface StepResource { url: string; title: string; }

function PathDetailContent() {
  const params = useParams();
  const pathId = params.id as string;
  const { data: pathDetails, isLoading, isError } = usePathDetails(pathId);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-3/4" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  // React Query سيتعامل مع خطأ 404 تلقائيًا إذا قمنا بإعداده، لكن notFound() هنا آمن أيضًا
  if (isError || !pathDetails) {
    return notFound();
  }

  return (
    <>
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-primary sm:text-4xl">{pathDetails.title}</h1>
        {pathDetails.description && (
          <p className="text-muted-foreground mt-2 text-lg">{pathDetails.description}</p>
        )}
      </div>

      <div className="space-y-6">
        {pathDetails.steps.map((step) => {
          let resource: StepResource | null = null;
          try {
            if (step.content) resource = JSON.parse(step.content);
          } catch (e) { console.error("Failed to parse content", e); }
          
          return (
            <StepItem
              key={step.id}
              stepId={step.id} // <-- سنحتاج هذا للمرحلة التالية
              stepNumber={step.step_number}
              title={step.title}
              resourceTitle={resource?.title || 'المورد غير متوفر'}
              resourceUrl={resource?.url || '#'}
              isCompleted={false} // <-- مؤقتًا، حتى نضيف منطق التتبع
              onComplete={() => {}} // <-- مؤقتًا
            />
          );
        })}
      </div>
      
      {pathDetails.steps.length === 0 && (
        <Alert>
          <Terminal className="h-4 w-4" />
          <AlertTitle>مسار فارغ</AlertTitle>
          <AlertDescription>هذا المسار التعليمي لا يحتوي على أي خطوات حاليًا.</AlertDescription>
        </Alert>
      )}
    </>
  );
}


export default function PathDetailPage() {
    return (
        <AuthGuard>
            <main className="container mx-auto max-w-4xl p-4 sm:p-8">
                <PathDetailContent />
            </main>
        </AuthGuard>
    );
}