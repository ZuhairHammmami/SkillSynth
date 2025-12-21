// المسار: src/app/paths/[id]/page.tsx
'use client';

import { useParams, notFound } from 'next/navigation';
import { usePathDetails } from '@/features/paths/hooks/usePathDetails';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import StepItem from '@/components/StepItem';
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal, AlertCircle } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { motion } from 'framer-motion';

function PathDetailContent() {
  const params = useParams();
  const pathId = params.id as string;
  const { data: pathDetails, isLoading, isError } = usePathDetails(pathId);

  // حالة التحميل الاحترافية
  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="text-center space-y-4">
            <Skeleton className="h-6 w-48 mx-auto" />
            <Skeleton className="h-12 w-3/4 mx-auto" />
            <Skeleton className="h-6 w-full max-w-2xl mx-auto" />
        </div>
        <div className="space-y-6">
            <Skeleton className="h-40 w-full rounded-lg" />
            <Skeleton className="h-40 w-full rounded-lg" />
            <Skeleton className="h-40 w-full rounded-lg" />
        </div>
      </div>
    );
  }

  // حالة الخطأ
  if (isError) {
    return (
        <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>حدث خطأ</AlertTitle>
            <AlertDescription>فشل في جلب تفاصيل المسار. يرجى المحاولة مرة أخرى.</AlertDescription>
        </Alert>
    );
  }

  // إذا لم يتم العثور على المسار بعد انتهاء التحميل
  if (!pathDetails) {
    return notFound();
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center mb-12">
        {/* =====> هذا هو التصحيح <===== */}
        {/* تحقق من وجود skills وأنها مصفوفة قبل استخدام map */}
        {pathDetails.skills && Array.isArray(pathDetails.skills) && (
            <div className="flex justify-center flex-wrap gap-2 mb-4">
            {pathDetails.skills.map(skill => (
                <Badge key={skill.id} variant="secondary" className="text-sm">
                    {skill.name}
                </Badge>
            ))}
            </div>
        )}
        {/* ============================== */}
        <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">{pathDetails.title}</h1>
        <p className="mt-6 max-w-3xl mx-auto text-lg text-muted-foreground">{pathDetails.description}</p>
      </div>
      
      {/* =====> وأيضًا هنا للخطوات <===== */}
      {pathDetails.steps && Array.isArray(pathDetails.steps) && pathDetails.steps.length > 0 ? (
        <div className="space-y-6">
          {pathDetails.steps.map((step) => (
            <StepItem key={step.id} step={step} />
          ))}
        </div>
      ) : (
        <Alert>
            <Terminal className="h-4 w-4" />
            <AlertTitle>مسار فارغ</AlertTitle>
            <AlertDescription>
                هذا المسار التعليمي لا يحتوي على أي خطوات حاليًا.
            </AlertDescription>
        </Alert>
      )}
    </motion.div>
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