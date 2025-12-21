// المسار: src/features/auth/components/ForgotPasswordForm.tsx
'use client';

import { useState } from 'react';
import { useForgotPassword } from '@/features/auth/hooks/useForgotPassword';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Loader2, MailCheck } from 'lucide-react';
import Link from 'next/link';

export default function ForgotPasswordForm() {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  // 1. استدعاء الـ Hook بدون أي وسائط
  const { mutate: performRequest, isPending } = useForgotPassword();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 2. تمرير البيانات ودالة onSuccess كخيار ثانٍ لدالة mutate
    performRequest(email, {
      onSuccess: () => {
        setIsSubmitted(true);
      },
    });
  };

  // واجهة النجاح التي تظهر بعد إرسال الطلب
  if (isSubmitted) {
    return (
        <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
            <Card className="w-full max-w-md text-center">
                <CardHeader className="items-center">
                    <div className="flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 text-primary">
                        <MailCheck className="h-8 w-8" />
                    </div>
                    <CardTitle className="text-2xl pt-4">تحقق من بريدك الإلكتروني</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground">
                        إذا كان البريد الإلكتروني الذي أدخلته صحيحًا، فستتلقى رابطًا لإعادة تعيين كلمة المرور خلال دقائق.
                    </p>
                </CardContent>
                <CardFooter>
                    <Button asChild className="w-full">
                        <Link href="/login">العودة لتسجيل الدخول</Link>
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
  }

  // الواجهة الأساسية للنموذج
  return (
    <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-2xl">استعادة كلمة المرور</CardTitle>
          <CardDescription>لا تقلق! أدخل بريدك الإلكتروني وسنساعدك.</CardDescription>
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
                disabled={isPending}
              />
            </div>
            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
              {isPending ? 'جارٍ الإرسال...' : 'إرسال رابط إعادة التعيين'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}