// المسار: src/features/user/components/ChangePasswordForm.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
// 1. استيراد الـ Hook ونوع البيانات
import { useChangePassword, ChangePasswordData } from '@/features/user/hooks/useChangePassword';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Loader2 } from 'lucide-react';
import type { FC } from 'react';

// 2. تعريف schema التحقق. لاحظ أننا لا نرسل `confirm_password` إلى الـ API.
const formSchema = z.object({
  current_password: z.string().min(1, { message: "كلمة المرور الحالية مطلوبة." }),
  new_password: z.string().min(8, { message: "كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل." }),
  confirm_password: z.string(),
}).refine(data => data.new_password === data.confirm_password, {
  message: "كلمتا المرور غير متطابقتين.",
  path: ["confirm_password"],
});

// 3. نستخدم Zod لاستنتاج نوع بيانات النموذج (بما في ذلك `confirm_password`)
type FormData = z.infer<typeof formSchema>;

export const ChangePasswordForm: FC = () => {
  const { mutate: performChange, isPending } = useChangePassword();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      current_password: "",
      new_password: "",
      confirm_password: "",
    },
  });

  // 4. دالة الإرسال الآن تعرف بالضبط ما هو نوع `values`
  function onSubmit(values: FormData) {
    // نمرر فقط البيانات التي يتوقعها الـ API، والتي تطابق النوع ChangePasswordData
    const dataToSend: ChangePasswordData = {
      current_password: values.current_password,
      new_password: values.new_password,
    };
    performChange(dataToSend);
    form.reset();
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="current_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>كلمة المرور الحالية</FormLabel>
              <FormControl>
                <Input type="password" {...field} disabled={isPending} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
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
        <Button type="submit" disabled={isPending} className="w-full sm:w-auto">
          {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
          {isPending ? 'جارٍ التغيير...' : 'تغيير كلمة المرور'}
        </Button>
      </form>
    </Form>
  );
};