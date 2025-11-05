// المسار: src/frontend/src/app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import PathCard from '@/app/components/PathCard'; // سنقوم بتحديث هذا المكون
import Link from 'next/link';
import { Button } from '@/components/ui/button';

// تعريف شكل بيانات المسار القادمة من الباك اند
interface LearningPath {
  id: number;
  path_title: string;
  total_estimated_hours: number;
  // أضف أي حقول أخرى تأتي من الباك اند
}

export default function DashboardPage() {
  const { token } = useAuth();
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPaths = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/paths/`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setPaths(response.data);
      } catch (err) {
        setError('فشل في جلب المسارات المحفوظة.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchPaths();
  }, [token]); // سيتم تشغيل هذا التأثير عند توفر التوكن

  if (isLoading) {
    return <div className="text-center p-10">⏳ جارٍ تحميل مساراتك...</div>;
  }

  if (error) {
    return <div className="text-center p-10 text-destructive">{error}</div>;
  }

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-primary">لوحة التحكم</h1>
        <Button asChild>
            <Link href="/wizard">
                أنشئ مسارًا جديدًا
            </Link>
        </Button>
      </div>

      {paths.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {paths.map((path) => (
            <PathCard
              key={path.id}
              id={path.id}
              title={path.path_title}
              totalHours={path.total_estimated_hours}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 border-2 border-dashed rounded-lg">
            <h3 className="text-xl font-semibold">لم تقم بإنشاء أي مسار بعد</h3>
            <p className="text-muted-foreground mt-2">ابدأ رحلتك التعليمية الآن!</p>
        </div>
      )}
    </div>
  );
}