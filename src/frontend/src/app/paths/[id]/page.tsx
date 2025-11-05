// المسار: src/frontend/src/app/paths/[id]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import StepItem from '@/app/components/StepItem';

// تعريف شكل البيانات المفصلة للمسار الواحد
interface StepResource {
  title: string;
  url: string;
  format: 'video' | 'article';
}
interface PathStep {
  index: number;
  title: string;
  estimated_hours: number;
  resource: StepResource | null;
}
interface PathDetails {
  path_title: string;
  steps: PathStep[];
  total_estimated_hours: number;
}

type PageProps = {
  params: { id: string };
};

export default function PathDetailPage({ params }: PageProps) {
  const { token } = useAuth();
  const [pathDetails, setPathDetails] = useState<PathDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPathDetails = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/paths/${params.id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setPathDetails(response.data);
      } catch (err) {
        setError('فشل في جلب تفاصيل المسار.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchPathDetails();
  }, [token, params.id]);

  if (isLoading) {
    return <div className="text-center p-10">⏳ جارٍ تحميل تفاصيل المسار...</div>;
  }

  if (error || !pathDetails) {
    return <div className="text-center p-10 text-destructive">{error || 'لم يتم العثور على المسار.'}</div>;
  }

  return (
    <main className="container mx-auto max-w-4xl p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-primary">{pathDetails.path_title}</h1>
        <p className="text-muted-foreground mt-2">
          إجمالي الساعات التقديرية: {pathDetails.total_estimated_hours} ساعة
        </p>
      </div>

      <div className="space-y-6">
        {pathDetails.steps.map((step) => (
          <StepItem
            key={step.index}
            title={step.title}
            description={`الساعات التقديرية: ${step.estimated_hours}`}
            resourceUrl={step.resource?.url || '#'}
          />
        ))}
      </div>
    </main>
  );
}