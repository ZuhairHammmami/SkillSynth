// app/components/Header.tsx
import Link from 'next/link';

type HeaderProps = {
  userName?: string; // Optional user name
};

export default function Header({ userName }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm">
      <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-blue-600">
          SkillSynth
        </Link>
        <div>
          {userName ? (
            <span className="text-gray-800">مرحباً، {userName}</span>
          ) : (
            <Link href="/login" className="text-blue-600 hover:underline">
              تسجيل الدخول
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}