// المسار: src/features/auth/components/ResetPasswordForm.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from "sonner"; // <--- 1. هذا هو السطر الناقص
import { Loader2 } from 'lucide-react';

interface Props {
  token: string;
}

export default function ResetPasswordForm({ token }: Props) {
    const router = useRouter();
    const [newPassword, setNewPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await apiClient.post('/api/auth/reset-password', {
              token: token,
              new_password: newPassword
            });
            toast.success("تم إعادة تعيين كلمة المرور بنجاح!");
            router.push('/login');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || "فشل إعادة التعيين. قد يكون الرابط منتهي الصلاحية.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
          <Card className="w-full max-w-sm">
            <CardHeader className="text-center space-y-1">
              <CardTitle className="text-2xl">إعادة تعيين كلمة المرور</CardTitle>
              <CardDescription>أدخل كلمة المرور الجديدة لحسابك.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="newPassword">كلمة المرور الجديدة</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    minLength={8}
                    disabled={isLoading}
                  />
                </div>
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
                  {isLoading ? 'جارٍ الحفظ...' : 'حفظ كلمة المرور الجديدة'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
    );
}