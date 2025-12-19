# 🚀 خطة إعادة الهيكلة النهائية لمشروع SkillSynth Frontend

**الهدف:** تحويل المشروع من هيكل عشوائي إلى بنية تحتية قوية، قابلة للصيانة، ومبنية على أفضل الممارسات باستخدام React Query و Feature-Sliced Design.

**قبل البدء:** تأكد من أنك قمت برفع كل التغييرات الحالية إلى GitHub.

---

### **المرحلة الأولى: إعادة هيكلة المجلدات وتأسيس React Query**

**الهدف:** بناء الهيكل الجديد وتنصيب الأدوات اللازمة.

**الخطوة 1.1: إنشاء هيكل المجلدات الجديد**

- في مجلد `src/`، أنشئ المجلدات التالية (إذا لم تكن موجودة):
  - `features/`
    - `auth/`
      - `components/`
    - `user/`
      - `components/`
    - `wizard/`
      - `components/`
  - `hooks/`

**الخطوة 1.2: نقل الملفات الموجودة إلى أماكنها الجديدة**

- **نقل صفحات المصادقة:**
  - انقل محتوى `src/app/(auth)/login/page.tsx` إلى `src/features/auth/components/LoginForm.tsx`.
  - انقل محتوى `src/app/(auth)/register/page.tsx` إلى `src/features/auth/components/RegisterForm.tsx`.
- **نقل صفحات الملف الشخصي:**
  - انقل `src/app/components/profile/UpdateProfileForm.tsx` إلى `src/features/user/components/UpdateProfileForm.tsx`.
  - انقل `src/app/components/profile/ChangePasswordForm.tsx` إلى `src/features/user/components/ChangePasswordForm.tsx`.
- **نقل مكونات الـ Wizard:**
  - انقل المجلد `src/app/components/wizard` بأكمله ليصبح `src/features/wizard/components`.

**الخطوة 1.3: إعداد React Query**

1.  **أنشئ ملف `src/lib/query-provider.tsx`:**
    ```tsx
    // المسار: src/lib/query-provider.tsx
    'use client';
    import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
    import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
    import { ReactNode, useState } from 'react';

    export function QueryProvider({ children }: { children: ReactNode }) {
      const [queryClient] = useState(() => new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            refetchOnWindowFocus: false,
          },
        },
      }));
      return (
        <QueryClientProvider client={queryClient}>
          {children}
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      );
    }
    ```
2.  **حدّث ملف `src/app/layout.tsx` ليستخدم الـ Provider:**
    ```tsx
    // المسار: src/app/layout.tsx
    import { QueryProvider } from '@/lib/query-provider';
    // ... other imports

    export default function RootLayout({ children }: { children: React.ReactNode }) {
      return (
        <html lang="ar" dir="rtl">
          <body>
            <QueryProvider> {/* <-- أضف هذا */}
              <AuthProvider>
                {/* ... بقية المحتوى ... */}
              </AuthProvider>
            </QueryProvider>
          </body>
        </html>
      );
    }
    ```

---

### **المرحلة الثانية: بناء نظام مصادقة وأدوار قوي**

**الهدف:** استبدال `AuthContext` بنظام مركزي يعتمد على React Query لإدارة بيانات المستخدم.

**الخطوة 2.1: إنشاء Hook لجلب بيانات المستخدم**

- **أنشئ ملف `src/features/user/hooks/useUser.ts`:**
  ```ts
  // المسار: src/features/user/hooks/useUser.ts
  import { useQuery } from '@tanstack/react-query';
  import apiClient from '@/lib/api';
  import Cookies from 'js-cookie';

  interface User { /* ... تعريف شكل المستخدم ... */ }

  const fetchUser = async (): Promise<User | null> => {
    const token = Cookies.get('authToken');
    if (!token) return null;
    try {
      const response = await apiClient.get<User>('/api/auth/users/me');
      return response.data;
    } catch (error) {
      Cookies.remove('authToken');
      return null;
    }
  };

  export const useUser = () => {
    return useQuery<User | null>({
      queryKey: ['user'],
      queryFn: fetchUser,
    });
  };