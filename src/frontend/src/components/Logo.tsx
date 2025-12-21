import React from 'react';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string; // لإصلاح الخطأ والسماح بالتنسيق الخارجي
  iconOnly?: boolean; // للتحكم في إظهار النص (مفيد للسايدبار)
}

export const Logo: React.FC<LogoProps> = ({ className, iconOnly = false }) => {
  return (
    <div className={cn("flex items-center gap-2 select-none", className)}>
      <div className="relative flex items-center justify-center">
        <svg
          width="32"
          height="32"
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full" // ليأخذ الحجم من الـ className الخارجي
        >
          {/* تعريف التدرج اللوني ليعطي فخامة */}
          <defs>
            <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="currentColor" />
              <stop offset="100%" stopColor="currentColor" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          
          {/* مسار يعبر عن حرف S وشكل المسار (Path) في نفس الوقت */}
          <path
            d="M8.5 22C8.5 24.4853 10.5147 26.5 13 26.5H19.5"
            stroke="url(#logo-gradient)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M23.5 10C23.5 7.51472 21.4853 5.5 19 5.5H12.5"
            stroke="url(#logo-gradient)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M8.5 22C8.5 17.5 12 17.5 12 13C12 8.5 15.5 8.5 15.5 8.5"
            stroke="url(#logo-gradient)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M23.5 10C23.5 14.5 20 14.5 20 19C20 23.5 16.5 23.5 16.5 23.5"
            stroke="url(#logo-gradient)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* نقاط الاتصال (Nodes) لتعبر عن الذكاء الاصطناعي */}
          <circle cx="16.5" cy="23.5" r="2" fill="currentColor" />
          <circle cx="15.5" cy="8.5" r="2" fill="currentColor" />
        </svg>
      </div>

      {/* إظهار النص فقط إذا لم نكن في وضع الأيقونة */}
      {!iconOnly && (
        <span className="font-bold text-xl tracking-tight text-foreground">
          SkillSynth
        </span>
      )}
    </div>
  );
};