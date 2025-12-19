// المسار: src/app/components/AnimatedBackground.tsx
'use client';
import { motion } from 'framer-motion';

export const AnimatedBackground = () => {
  return (
    <div className="absolute top-0 left-0 -z-10 h-full w-full bg-white">
      <div className="absolute bottom-auto left-auto right-0 top-0 h-[500px] w-[500px] -translate-x-[30%] translate-y-[20%] rounded-full bg-[rgba(59,130,246,0.5)] opacity-50 blur-[80px]"></div>
    </div>
  );
};