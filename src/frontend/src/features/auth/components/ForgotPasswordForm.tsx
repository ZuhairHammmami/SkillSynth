// المسار: src/app/(auth)/forgot-password/page.tsx
'use client';

import { useState } from 'react';
import apiClient from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await apiClient.post('/api/auth/request-password-reset', { email });
      setIsSubmitted(true); // اعرض رسالة النجاح
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "فشل إرسال الطلب. تأكد من البريد الإلكتروني.");
    } finally {
      setIsLoading(false);
    }
  };

  // عرض رسالة نجاح بعد إرسال الطلب
  if (isSubmitted) {
    return (
        <div className="container mx-auto flex items-center justify-center min-h-[calc(100vh-80px)] px-4">
            <Card className="w-full max-w-md text-center">
                <CardHeader>
                    <CardTitle className="text-2xl">📧 تم إرسال الرابط</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground">
                        إذا كان البريد الإلكتروني الذي أدخلته موجودًا في نظامنا، فستتلقى رابطًا لإعادة تعيين كلمة المرور قريبًا.
                    </p>
                    <Button asChild className="mt-6">
                        <Link href="/login">العودة لتسجيل الدخول</Link>
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
  }

  return (
    <div className="container mx-auto flex items-center justify-center min-h-[calc(100vh-80px)] px-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center space-y-1">
          <CardTitle className="text-2xl">استعادة كلمة المرور</CardTitle>
          <CardDescription>أدخل بريدك الإلكتروني وسنرسل لك رابطًا لإعادة التعيين.</CardDescription>
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
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
              {isLoading ? 'جارٍ الإرسال...' : 'إرسال رابط إعادة التعيين'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}