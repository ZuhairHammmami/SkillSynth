// المسار: src/app/(auth)/reset-password/[token]/page.tsx
'use client'; // <-- مهم للصفحات الديناميكية التي تستخدم props
import ResetPasswordForm from '@/features/auth/components/ResetPasswordForm';

export default function ResetPasswordTokenPage({ params }: { params: { token: string } }) {
  // نقوم بتمرير التوكن من الرابط إلى المكون
  return <ResetPasswordForm token={params.token} />;
}