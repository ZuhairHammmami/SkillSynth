// المسار: src/app/paths/[id]/page.tsx
'use client';

import { useEffect, useState } from 'react';
// 1. استيراد useParams
import { notFound, useParams } from 'next/navigation';
import apiClient from '@/lib/api';
import StepItem from '@/app/components/StepItem';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Terminal } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

// ... تعريف أنواع البيانات يبقى كما هو ...
interface StepResource { url: string; title: string; }
interface PathStep { step_number: number; title: string; content: string; }
interface PathDetails { id: number; title: string; description: string | null; steps: PathStep[]; }

// 2. لم نعد بحاجة لتعريف PageProps
// type PageProps = { params: { id: string } };

export default function PathDetailPage() { // <-- إزالة props من هنا
  // 3. استخدام useParams للحصول على الـ id بأمان
  const params = useParams();
  const pathId = params.id as string; // نحوله إلى string

  const { isAuthenticated } = useAuth();
  const [pathDetails, setPathDetails] = useState<PathDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPathDetails = async () => {
      try {
        // 4. استخدام pathId الذي حصلنا عليه من useParams
        const response = await apiClient.get<PathDetails>(`/api/paths/${pathId}`);
        setPathDetails(response.data);
      } catch (err: any) {
        if (err.response?.status === 404) {
          return notFound();
        }
        setError('حدث خطأ أثناء جلب تفاصيل المسار.');
      } finally {
        setIsLoading(false);
      }
    };

    // الشرط الحاسم: لا تقم بالطلب إلا بوجود ID ومستخدم مصادق عليه
    if (isAuthenticated && pathId) {
      fetchPathDetails();
    } else if (!isAuthenticated) {
      setIsLoading(false);
    }
  }, [pathId, isAuthenticated]); // 5. تحديث مصفوفة التبعيات

  // ... بقية الكود يبقى كما هو ...
  if (isLoading) {
    return <div className="text-center p-10">⏳ جارٍ التحميل...</div>;
  }
  if (error) {
    return <div className="container mx-auto p-8 text-center text-destructive">{error}</div>;
  }
  if (!pathDetails) {
    return notFound();
  }

  return (
    <main className="container mx-auto max-w-4xl p-4 sm:p-8">
      {/* ... JSX يبقى كما هو ... */}
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
            if (step.content) {
                resource = JSON.parse(step.content);
            }
          } catch (e) {
            console.error("Failed to parse step content:", step.content, e);
          }
          return (
            <StepItem
              key={step.step_number}
              stepNumber={step.step_number}
              title={step.title}
              resourceTitle={resource?.title || 'المورد غير متوفر'}
              resourceUrl={resource?.url || '#'}
            />
          );
        })}
      </div>
    </main>
  );
} 