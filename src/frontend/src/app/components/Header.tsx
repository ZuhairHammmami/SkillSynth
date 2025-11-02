// المسار: src/frontend/src/app/components/Header.tsx

import Link from 'next/link';
import { Button } from '@/components/ui/button'; // <-- استيراد الزر الجديد

type HeaderProps = {
  userName?: string;
};

export default function Header({ userName }: HeaderProps) {
  return (
    <header className="bg-background sticky top-0 z-50 w-full border-b">
      <nav className="container mx-auto px-6 py-3 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-primary">
          SkillSynth
        </Link>
        <div>
          {userName ? (
            <span className="text-foreground">مرحباً، {userName}</span>
          ) : (
            <Button asChild variant="ghost">
              <Link href="/login">تسجيل الدخول</Link>
            </Button>
          )}
        </div>
      </nav>
    </header>
  );
}