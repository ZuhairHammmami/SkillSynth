import Link from 'next/link';
import { cn } from '@/shared/lib/utils';

interface LogoProps {
  href?: string;
  className?: string;
  iconOnly?: boolean;
}

export function Logo({ href = '/', className, iconOnly }: LogoProps) {
  return (
    <Link href={href} className={cn("flex items-center gap-2", className)}>
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-bold">
        S
      </div>
      {!iconOnly && (
        <span className="text-lg font-semibold tracking-tight">SkillSynth</span>
      )}
    </Link>
  );
}
