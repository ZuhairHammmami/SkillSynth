// المسار: src/components/ClientAppInitializer.tsx
'use client';

import { useUser } from '@/features/user/hooks/useUser';

/**
 * هذا المكون لا يعرض أي شيء.
 * مهمته الوحيدة هي استدعاء `useUser` عند تحميل التطبيق،
 * والذي بدوره سيقوم بجلب بيانات المستخدم وتحديث مخزن Zustand.
 */
export function ClientAppInitializer() {
  useUser();
  return null;
}