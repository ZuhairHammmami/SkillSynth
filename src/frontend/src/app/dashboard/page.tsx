// المسار: src/frontend/src/app/dashboard/page.tsx
'use client';
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api';
import PathCard from '@/app/components/PathCard';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

// =====> هذا هو التصحيح المهم <=====
// تعريف شكل البيانات الصحيح بناءً على ما يرسله الباك اند
interface LearningPath {
  id: number;
  title: string; // <-- الباك اند يرسل 'title'، وليس 'path_title'
  total_estimated_hours: number;
}
// ===================================

export default function DashboardPage() {
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPaths = async () => {
      try {
        const response = await apiClient.get<LearningPath[]>('/api/paths/');
        setPaths(response.data);
      } catch (err) {
        setError('فشل في جلب المسارات المحفوظة.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchPaths();
  }, []);

  if (isLoading) {
    return <div className="text-center p-10">⏳ جارٍ تحميل مساراتك...</div>;
  }

  if (error) {
    return <div className="container p-8 text-center text-destructive">{error}</div>;
  }

  return (
    <div className="container mx-auto p-4 sm:p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">لوحة التحكم</h1>
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
              title={path.title} // <-- الآن نستخدم 'title' الصحيح
              totalHours={path.total_estimated_hours}
            />
          ))}
        </div>
      ) : (
        <Card className="mt-10">
          <CardHeader>
            <CardTitle>مرحباً بك في SkillSynth!</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">لم تقم بإنشاء أي مسار تعليمي بعد. ابدأ رحلتك الآن بالضغط على زر "أنشئ مسارًا جديدًا".</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}