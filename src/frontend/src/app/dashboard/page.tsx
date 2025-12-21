// المسار: src/app/dashboard/page.tsx
'use client';

import { usePaths } from '@/features/paths/hooks/usePaths';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import PathCard from '@/components/PathCard';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { EmptyStateIllustration } from '@/components/EmptyStateIllustration';
import { Skeleton } from '@/components/ui/skeleton';
import { motion } from 'framer-motion';

// المكون الداخلي الذي يعرض المحتوى
function DashboardContent() {
  const { data: paths, isLoading, isError, error } = usePaths();

  // حالة التحميل
  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="p-6 rounded-lg border bg-card space-y-4">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return <div className="text-center text-destructive py-10">{error.message}</div>;
  }

  // تعريفات التحريك
  const containerVariants = {
    hidden: { opacity: 1 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };
  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 },
  };

  return (
    <>
      {paths && paths.length > 0 ? (
        <motion.div 
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {paths.map((path) => (
            <motion.div key={path.id} variants={itemVariants}>
              <PathCard
                id={path.id}
                title={path.title}
                totalHours={path.total_estimated_hours}
              />
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <div className="text-center py-16 mt-10 border-2 border-dashed rounded-lg flex flex-col items-center justify-center gap-4">
          <EmptyStateIllustration />
          <h3 className="text-xl font-semibold mt-4">ابدأ رحلتك التعليمية</h3>
          <p className="text-muted-foreground max-w-md">لم تقم بإنشاء أي مسار بعد. انقر على الزر أعلاه لتوليد أول مسار تعليمي مخصص لك.</p>
        </div>
      )}
    </>
  );
}

// المكون الرئيسي للصفحة
export default function DashboardPage() {
  return (
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
        <DashboardContent />
      </div>
    </AuthGuard>
  );
}