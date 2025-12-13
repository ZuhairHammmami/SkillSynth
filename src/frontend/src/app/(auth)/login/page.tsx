// المسار: src/frontend/src/app/(auth)/login/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api'; // <-- نستخدم عميل API المركزي
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // الباك اند يتوقع بيانات form-urlencoded هنا
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    params.append('grant_type', 'password');

    try {
      const response = await apiClient.post('/api/auth/token', params, {
        // نحدد نوع المحتوى يدويًا لأننا لا نرسل JSON
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      // عند النجاح، نستخدم دالة login من السياق
      await login(response.data.access_token);
      // نوجه المستخدم إلى لوحة التحكم بعد تسجيل الدخول بنجاح
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'فشل تسجيل الدخول. تأكد من صحة بياناتك.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // هذا الكود يضمن أن النموذج سيكون في منتصف الصفحة عموديًا وأفقيًا
    <div className="container mx-auto flex items-center justify-center min-h-[calc(100vh-80px)] px-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center space-y-1">
          <CardTitle className="text-2xl">تسجيل الدخول</CardTitle>
          <CardDescription>أدخل بياناتك للوصول إلى حسابك</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">البريد الإلكتروني</Label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">كلمة المرور</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            {error && <p className="text-sm font-medium text-destructive">{error}</p>}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'جارٍ التحقق...' : 'دخول'}
            </Button>
          </form>
        </CardContent>
        <CardFooter>
          <p className="text-center text-sm text-muted-foreground w-full">
            ليس لديك حساب؟{' '}
            <Link href="/register" className="font-semibold text-primary hover:underline">
              أنشئ حسابًا جديدًا
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}