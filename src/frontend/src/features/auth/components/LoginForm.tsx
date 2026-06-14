'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useLogin } from '../hooks/useLogin';
import Link from 'next/link';
// import { useRouter } from 'next/navigation'; // <-- لم نعد بحاجة لهذا هنا
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/shared/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/ui/form";
import { Loader2 } from 'lucide-react';
import { Logo } from '@/shared/components/Logo';

// تعريف schema التحقق باستخدام Zod
const formSchema = z.object({
  email: z.string().email({ message: "الرجاء إدخال بريد إلكتروني صالح." }),
  password: z.string().min(1, { message: "كلمة المرور مطلوبة." }),
});

export default function LoginForm() {
  // const router = useRouter(); // <-- إزالة
  
  // استدعاء الـ Hook الخاص بتسجيل الدخول
  const { mutate: performLogin, isPending } = useLogin();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    // التغيير هنا: قمنا بإزالة onSuccess وتمرير القيم فقط
    // سيقوم useLogin بالتعامل مع التوجيه بناءً على دور المستخدم
    performLogin(values);
  }

  return (
    <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center space-y-4">
          <Link href="/" className="inline-block mx-auto">
            <Logo />
          </Link>
          <CardTitle className="text-2xl">تسجيل الدخول</CardTitle>
          <CardDescription>مرحباً بعودتك! أدخل بياناتك للمتابعة.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>البريد الإلكتروني</FormLabel>
                    <FormControl>
                      <Input placeholder="name@example.com" {...field} disabled={isPending} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <div className="flex items-center justify-between">
                      <FormLabel>كلمة المرور</FormLabel>
                      <Link href="/forgot-password" className="text-sm font-medium text-primary hover:underline">
                        نسيت كلمة المرور؟
                      </Link>
                    </div>
                    <FormControl>
                      <Input type="password" {...field} disabled={isPending} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={isPending}>
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {isPending ? 'جارٍ التحقق...' : 'دخول'}
              </Button>
            </form>
          </Form>
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