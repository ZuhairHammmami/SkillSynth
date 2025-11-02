// app/page.tsx
import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">SkillSynth</h1>
        <p className="text-lg text-gray-600 mb-8">
          أنشئ مسار تعلمك المخصص والذكي
        </p>
        <Link href="/wizard">
          <button className="bg-blue-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-blue-700 transition-colors">
            ابدأ الآن
          </button>
        </Link>
      </div>
    </main>
  );
}