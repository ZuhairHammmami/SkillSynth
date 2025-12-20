// المسار: src/features/auth/components/ForgotPasswordForm.tsx
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

export default function ForgotPasswordForm() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await apiClient.post('/api/auth/request-password-reset', { email });
      setIsSubmitted(true);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "فشل إرسال الطلب.");
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isSubmitted) { /* ... JSX لرسالة النجاح ... */ }

  return (
    <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
      <Card className="w-full max-w-sm">
        {/* ... JSX للنموذج ... */}
      </Card>
    </div>
  );
}