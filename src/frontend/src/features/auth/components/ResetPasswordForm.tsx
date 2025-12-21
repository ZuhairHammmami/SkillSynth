// المسار: src/features/auth/components/ResetPasswordForm.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { useResetPassword } from '@/features/auth/hooks/useResetPassword';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import type { FC } from 'react';

// تعريف schema التحقق
const formSchema = z.object({
  new_password: z.string().min(8, { message: "كلمة المرور يجب أن تكون 8 أحرف على الأقل." }),
  confirm_password: z.string(),
}).refine(data => data.new_password === data.confirm_password, {
  message: "كلمتا المرور غير متطابقتين.",
  path: ["confirm_password"],
});

type FormData = z.infer<typeof formSchema>;

interface Props {
  token: string;
}

const ResetPasswordForm: FC<Props> = ({ token }) => {
  const router = useRouter();
  
  // 1. استدعاء الـ Hook بدون أي وسائط
  const { mutate: performReset, isPending } = useResetPassword();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: { new_password: "", confirm_password: "" },
  });

  function onSubmit(values: FormData) {
    // 2. تمرير البيانات ودالة onSuccess كخيار ثانٍ لدالة mutate
    performReset({
      token: token,
      new_password: values.new_password,
    }, {
        onSuccess: () => {
            // بعد 3 ثوانٍ، أعد توجيه المستخدم لصفحة تسجيل الدخول
            setTimeout(() => {
                router.push('/login');
            }, 3000);
        }
    });
  }

  return (
    <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center space-y-2">
          <CardTitle className="text-2xl">إعادة تعيين كلمة المرور</CardTitle>
          <CardDescription>أدخل كلمة المرور الجديدة لحسابك.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="new_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>كلمة المرور الجديدة</FormLabel>
                    <FormControl>
                      <Input type="password" {...field} disabled={isPending} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="confirm_password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>تأكيد كلمة المرور الجديدة</FormLabel>
                    <FormControl>
                      <Input type="password" {...field} disabled={isPending} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={isPending}>
                {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
                {isPending ? 'جارٍ الحفظ...' : 'حفظ كلمة المرور الجديدة'}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
};

export default ResetPasswordForm;