// المسار: src/frontend/src/app/page.tsx
'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { useAuth } from '@/context/AuthContext'; // نستدعي الدماغ لنعرف حالة المستخدم

export default function LandingPage() {
  const { isAuthenticated } = useAuth(); // نحصل على حالة تسجيل الدخول

  return (
    <div className="container mx-auto flex flex-col items-center justify-center text-center px-4 py-24 sm:py-32">
      <h1 className="text-4xl font-bold tracking-tight text-primary sm:text-5xl md:text-6xl">
        SkillSynth
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
        حوّل أهدافك إلى خطة عمل واضحة وفعالة. أنشئ مسار تعلمك المخصص والذكي
        المدعوم بالذكاء الاصطناعي.
      </p>
      <div className="mt-10">
        {/* نعرض زرًا مختلفًا بناءً على حالة تسجيل الدخول */}
        {isAuthenticated ? (
          <Button asChild size="lg">
            <Link href="/dashboard">
              اذهب إلى لوحة التحكم
              <ArrowLeft className="mr-2 h-5 w-5" />
            </Link>
          </Button>
        ) : (
          <Button asChild size="lg">
            <Link href="/login">
              ابدأ الآن
              <ArrowLeft className="mr-2 h-5 w-5" />
            </Link>
          </Button>
        )}
      </div>
    </div>
  );
}