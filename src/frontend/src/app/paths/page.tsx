'use client';

import { usePaths } from '@/features/paths/hooks/usePaths';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import PathCard from '@/shared/components/PathCard';
import Link from 'next/link';
import { Button } from '@/shared/ui/button';
import { EmptyStateIllustration } from '@/shared/components/EmptyStateIllustration';
import { DashboardGridSkeleton } from '@/shared/components/SkeletonLoading';
import { motion } from 'framer-motion';
import { memo } from 'react';

const ANIMATION_VARIANTS = {
  container: {
    hidden: { opacity: 1 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  },
  item: {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 },
  },
};

const PathsContent = memo(function PathsContent() {
  const { data: paths, isLoading, isError, error } = usePaths();

  if (isLoading) {
    return <DashboardGridSkeleton count={3} />;
  }

  if (isError) {
    return <div className="text-center text-destructive py-10">{error?.message || 'حدث خطأ في تحميل المسارات'}</div>;
  }

  return (
    <>
      {paths && paths.length > 0 ? (
        <motion.div
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
          variants={ANIMATION_VARIANTS.container}
          initial="hidden"
          animate="visible"
        >
          {paths.map((path) => (
            <motion.div key={path.id} variants={ANIMATION_VARIANTS.item}>
              <PathCard
                id={path.id}
                title={path.title}
                totalHours={path.total_estimated_hours ?? path.total_hours ?? 0}
              />
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <div className="text-center py-16 mt-10 border-2 border-dashed rounded-lg flex flex-col items-center justify-center gap-4">
          <EmptyStateIllustration />
          <h3 className="text-xl font-semibold mt-4">ابدأ رحلتك التعليمية</h3>
          <p className="text-muted-foreground max-w-md">لم تقم بإنشاء أي مسار بعد. استخدم المعالج الذكي لإنشاء أول مسار تعليمي مخصص لك.</p>
          <Button asChild>
            <Link href="/wizard">إنشاء مسار جديد</Link>
          </Button>
        </div>
      )}
    </>
  );
});

export default function PathsPage() {
  return (
    <AuthGuard>
      <div className="container mx-auto p-4 sm:p-8">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold">مساراتي التعليمية</h1>
            <p className="text-muted-foreground mt-1">جميع مساراتك التعليمية في مكان واحد</p>
          </div>
          <Button asChild>
            <Link href="/wizard">مسار جديد</Link>
          </Button>
        </div>
        <PathsContent />
      </div>
    </AuthGuard>
  );
}
