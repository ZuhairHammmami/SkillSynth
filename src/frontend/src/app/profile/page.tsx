// المسار: src/app/profile/page.tsx
'use client';

import { useAuth } from '@/context/AuthContext';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { UpdateProfileForm } from '@/app/components/profile/UpdateProfileForm';
import { ChangePasswordForm } from '@/app/components/profile/ChangePasswordForm';
import { Skeleton } from '@/components/ui/skeleton';

export default function ProfilePage() {
  const { user, isLoading } = useAuth();

  // عرض هيكل عظمي احترافي أثناء التحقق من المستخدم
  if (isLoading) {
    return (
      <div className="container mx-auto py-10 max-w-2xl">
        <div className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-[400px] w-full" />
        </div>
      </div>
    );
  }

  // إذا انتهى التحميل ولم يكن هناك مستخدم، لا تعرض شيئًا (Middleware سيتولى إعادة التوجيه)
  if (!user) {
    return null;
  }

  return (
    <div className="container mx-auto py-10 max-w-2xl">
      <Tabs defaultValue="profile">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="profile">الملف الشخصي</TabsTrigger>
          <TabsTrigger value="password">الأمان</TabsTrigger>
        </TabsList>
        <TabsContent value="profile" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>الملف الشخصي</CardTitle>
              <CardDescription>
                تحديث معلومات حسابك. سيتم استخدام اسمك الكامل في جميع أنحاء التطبيق.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <UpdateProfileForm user={user} />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="password" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>تغيير كلمة المرور</CardTitle>
              <CardDescription>
                اختر كلمة مرور جديدة وقوية. نوصي بتغييرها بشكل دوري للحفاظ على أمان حسابك.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChangePasswordForm />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}