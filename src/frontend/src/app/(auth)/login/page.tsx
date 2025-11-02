// المسار: src/frontend/src/app/(auth)/login/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext'; // 1. استيراد "الدماغ"
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth(); // 2. الحصول على دالة login لتخزين التوكن

  // States لحقول النموذج وحالة الطلب
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // 3. ملاحظة هامة: الباك اند يتوقع بيانات form-urlencoded هنا، وليس JSON
    const params = new URLSearchParams();
    params.append('username', email); // الباك اند يتوقع 'username' كبريد إلكتروني
    params.append('password', password);
    params.append('grant_type', 'password'); // قيمة ثابتة مطلوبة من الباك اند

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/token`,
        params, // 4. إرسال البيانات بصيغة form-urlencoded
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      // 5. عند النجاح، احصل على التوكن وقم بتخزينه
      const { access_token } = response.data;
      login(access_token); // <-- هنا يتم حفظ التوكن في "الدماغ"

      // 6. وجه المستخدم إلى صفحة المعالج لبدء العمل
      router.push('/wizard');

    } catch (err: any) {
      console.error('Login Error:', err);
      setError(err.response?.data?.detail || 'فشل تسجيل الدخول. تأكد من بياناتك.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto flex items-center justify-center py-24">
      <form
        onSubmit={handleSubmit}
        className="p-8 bg-card text-card-foreground rounded-lg border shadow-lg space-y-6 w-full max-w-sm"
      >
        <div className="text-center">
            <h2 className="text-2xl font-bold text-primary">تسجيل الدخول</h2>
        </div>
        
        <div className="grid w-full items-center gap-1.5">
          <Label htmlFor="email">البريد الإلكتروني</Label>
          <Input
            id="email"
            type="email"
            placeholder="email@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        
        <div className="grid w-full items-center gap-1.5">
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
        
        {error && (
            <p className="text-sm font-medium text-destructive bg-destructive/10 p-2 rounded">
            {error}
            </p>
        )}
        
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'جارٍ التحقق...' : 'دخول'}
        </Button>
      </form>
    </div>
  );
}