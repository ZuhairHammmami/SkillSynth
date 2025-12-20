// المسار: src/app/profile/page.tsx
'use client';
import { useAuthStore } from '@/store/authStore';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { UpdateProfileForm } from '@/features/user/components/UpdateProfileForm';
import { ChangePasswordForm } from '@/features/user/components/ChangePasswordForm';
import { Skeleton } from '@/components/ui/skeleton';

function ProfileContent() {
  const { user } = useAuthStore();

  // هذا الشرط ضروري لأن AuthGuard يضمن وجود المستخدم
  if (!user) return null; 

  return (
    <Tabs defaultValue="profile">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="profile">الملف الشخصي</TabsTrigger>
        <TabsTrigger value="password">الأمان</TabsTrigger>
      </TabsList>
      <TabsContent value="profile" className="mt-4">
        <Card>
          <CardHeader>
            <CardTitle>الملف الشخصي</CardTitle>
            <CardDescription>تحديث معلومات حسابك.</CardDescription>
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
            <CardDescription>اختر كلمة مرور جديدة وقوية.</CardDescription>
          </CardHeader>
          <CardContent>
            <ChangePasswordForm />
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}

export default function ProfilePage() {
    return (
        <AuthGuard>
            <div className="container mx-auto py-10 max-w-2xl">
                <ProfileContent />
            </div>
        </AuthGuard>
    );
}