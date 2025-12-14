// المسار: src/frontend/src/app/dashboard/page.tsx
'use client';
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api';
import PathCard from '@/app/components/PathCard';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { EmptyStateIllustration } from '@/app/components/EmptyStateIllustration';

interface LearningPath {
  id: number;
  title: string;
  total_estimated_hours: number;
}

export default function DashboardPage() {
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient.get<LearningPath[]>('/api/paths/')
      .then(response => setPaths(response.data))
      .catch(() => setError('فشل في جلب المسارات المحفوظة.'))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <div className="text-center container mx-auto p-8">⏳ جارٍ التحميل...</div>;
  if (error) return <div className="container mx-auto p-8 text-center text-destructive">{error}</div>;

  return (
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

      {paths.length > 0 ? (
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
        <div className="text-center py-16 mt-10 border-2 border-dashed rounded-lg flex flex-col items-center justify-center gap-4">
            <EmptyStateIllustration />
            <h3 className="text-xl font-semibold mt-4">ابدأ رحلتك التعليمية</h3>
            <p className="text-muted-foreground max-w-md">لم تقم بإنشاء أي مسار بعد. انقر على الزر أعلاه لتوليد أول مسار تعليمي مخصص لك.</p>
        </div>
      )}
    </div>
  );
}