// المسار: src/frontend/src/app/(auth)/register/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/register`,
        {
          full_name: fullName,
          email: email,
          password: password,
        }
      );
      // عند النجاح، وجه المستخدم إلى صفحة تسجيل الدخول ليكمل العملية
      router.push('/login');

    } catch (err: any) {
      console.error('Registration Error:', err);
      setError(err.response?.data?.detail || 'فشل إنشاء الحساب. قد يكون البريد الإلكتروني مستخدمًا.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto flex items-center justify-center py-16">
      <form
        onSubmit={handleSubmit}
        className="p-8 bg-card text-card-foreground rounded-lg border shadow-lg space-y-6 w-full max-w-sm"
      >
        <div className="text-center">
            <h2 className="text-2xl font-bold text-primary">إنشاء حساب جديد</h2>
        </div>
        
        <div className="grid w-full items-center gap-1.5">
          <Label htmlFor="fullName">الاسم الكامل</Label>
          <Input id="fullName" value={fullName} onChange={(e) => setFullName(e.target.value)} required disabled={isLoading} />
        </div>
        
        <div className="grid w-full items-center gap-1.5">
          <Label htmlFor="email">البريد الإلكتروني</Label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required disabled={isLoading} />
        </div>
        
        <div className="grid w-full items-center gap-1.5">
          <Label htmlFor="password">كلمة المرور</Label>
          <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required disabled={isLoading} />
        </div>
        
        {error && <p className="text-sm font-medium text-destructive">{error}</p>}
        
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'جارٍ الإنشاء...' : 'تسجيل'}
        </Button>

        <p className="text-center text-sm text-muted-foreground">
            لديك حساب بالفعل؟{' '}
            <Link href="/login" className="font-semibold text-primary hover:underline">
                سجل الدخول
            </Link>
        </p>
      </form>
    </div>
  );
}