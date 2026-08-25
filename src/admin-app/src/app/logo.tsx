import Link from 'next/link';

export function Logo() {
  return (
    <Link href="/dashboard" className="flex items-center gap-2">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-bold">
        S
      </div>
      <span className="text-lg font-semibold tracking-tight">SkillSynth</span>
    </Link>
  );
}
