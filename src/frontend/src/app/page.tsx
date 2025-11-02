// المسار: src/frontend/src/app/page.tsx

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react'; // <-- استيراد أيقونة السهم

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center text-center px-4 py-24 md:py-32">
      <h1 className="text-4xl font-bold tracking-tight text-primary sm:text-5xl md:text-6xl">
        SkillSynth
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
        أنشئ مسار تعلمك المخصص والذكي. حوّل أهدافك إلى خطة عمل واضحة وفعالة
        مدعومة بالذكاء الاصطناعي.
      </p>
      <div className="mt-10">
        <Button asChild size="lg">
          <Link href="/wizard">
            ابدأ الآن
            <ArrowLeft className="mr-2 h-5 w-5" />
          </Link>
        </Button>
      </div>
    </div>
  );
}