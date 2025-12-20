// المسار: src/app/dashboard/page.tsx
'use client';

import { usePaths } from '@/features/paths/hooks/usePaths';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import PathCard from '@/components/PathCard'; // <-- تم نقله
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { EmptyStateIllustration } from '@/components/EmptyStateIllustration'; // <-- تم نقله
import { Skeleton } from '@/components/ui/skeleton';

// هذا المكون هو "القلب" الفعلي للصفحة، ويتم عرضه فقط بعد التحقق من المصادقة
function DashboardContent() {
  const { data: paths, isLoading, isError, error } = usePaths();

  // حالة التحميل أثناء جلب المسارات
  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* عرض 3 هياكل عظمية للبطاقات */}
        <Skeleton className="h-32 w-full rounded-lg" />
        <Skeleton className="h-32 w-full rounded-lg" />
        <Skeleton className="h-32 w-full rounded-lg" />
      </div>
    );
  }

  // حالة حدوث خطأ أثناء الجلب
  if (isError) {
    return <div className="text-center text-destructive">فشل في جلب المسارات: {error.message}</div>;
  }

  return (
    <>
      {paths && paths.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {paths.map((path) => (
            <PathCard
              key={path.id}
              id={path.id}
              title={path.title}
              totalHours={path.total_estimated_hours}
            />
          ))}
        </div>
      ) : (
        // حالة عدم وجود مسارات
        <div className="text-center py-16 mt-10 border-2 border-dashed rounded-lg flex flex-col items-center justify-center gap-4">
          <EmptyStateIllustration />
          <h3 className="text-xl font-semibold mt-4">ابدأ رحلتك التعليمية</h3>
          <p className="text-muted-foreground max-w-md">لم تقم بإنشاء أي مسار بعد. انقر على الزر أعلاه لتوليد أول مسار تعليمي مخصص لك.</p>
        </div>
      )}
    </>
  );
}

// هذا هو المكون الرئيسي للصفحة
export default function DashboardPage() {
  return (
    // 1. نلف كل شيء بـ AuthGuard لحماية الصفحة
    <AuthGuard>
      <div className="container mx-auto p-4 sm:p-8">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 mb-8">
          <div>
              <h1 className="text-3xl font-bold">لوحة التحكم</h1>
              <p className="text-muted-foreground mt-1">مساراتك التعليمية المحفوظة</p>
          </div>
          <Button asChild>
            <Link href="/wizard">أنشئ مسارًا جديدًا</Link>
          </Button>
        </div>
        {/* 2. نعرض المحتوى الفعلي للصفحة */}
        <DashboardContent />
      </div>
    </AuthGuard>
  );
}