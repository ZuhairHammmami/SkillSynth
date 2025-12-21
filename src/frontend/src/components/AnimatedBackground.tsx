'use client';

export const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 -z-50 overflow-hidden bg-slate-950">
      {/* 1. شبكة خلفية ثابتة */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />

      {/* 2. أضواء متحركة (Spotlights) */}
      <div className="absolute top-0 left-0 right-0 h-[500px] bg-gradient-to-b from-cyan-500/10 via-blue-500/5 to-transparent blur-3xl" />
      
      {/* 3. عناصر عائمة (Orbiting Elements) - تعبر عن المهارات */}
      <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-500/20 rounded-full blur-2xl animate-pulse delay-75" />
      <div className="absolute bottom-1/3 right-1/4 w-40 h-40 bg-purple-500/20 rounded-full blur-2xl animate-pulse delay-1000" />

      {/* 4. خطوط المسار (SVG Lines) */}
      <svg className="absolute inset-0 w-full h-full opacity-20" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#3b82f6', stopOpacity: 0 }} />
            <stop offset="50%" style={{ stopColor: '#06b6d4', stopOpacity: 1 }} />
            <stop offset="100%" style={{ stopColor: '#3b82f6', stopOpacity: 0 }} />
          </linearGradient>
        </defs>
        {/* مسار منحني 1 */}
        <path 
            d="M0,100 Q400,300 800,100 T1600,300" 
            fill="none" 
            stroke="url(#grad1)" 
            strokeWidth="2"
            className="animate-dash"
        />
      </svg>
    </div>
  );
};