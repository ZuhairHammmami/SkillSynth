'use client';

import { memo } from 'react';

/**
 * AnimatedBackground - Memoized decorative background with blob animations
 * 
 * Performance: 
 * - Wrapped with React.memo to prevent unnecessary re-renders
 * - No props means identity never changes
 * - CSS animations are GPU-accelerated (not JavaScript-based)
 * - Local noise.svg avoids CDN dependency
 */
export const AnimatedBackground = memo(function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-50 overflow-hidden bg-[#0f172a]">
      
      {/* Blob 1: Sky Blue - animation-delay-0 (default) */}
      <div 
        className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-blue-500/20 rounded-full blur-[100px] mix-blend-screen animate-blob"
      />
      
      {/* Blob 2: Indigo - animation-delay-2000 */}
      <div 
        className="absolute top-[40%] right-[-10%] w-[400px] h-[400px] bg-indigo-500/20 rounded-full blur-[100px] mix-blend-screen animate-blob animation-delay-2000"
      />
      
      {/* Blob 3: Cyan - animation-delay-4000 */}
      <div 
        className="absolute bottom-[-10%] left-[20%] w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[120px] mix-blend-screen animate-blob animation-delay-4000"
      />

      {/* Subtle grain texture - using local SVG */}
      <div className="absolute inset-0 bg-[url('/noise.svg')] opacity-10"></div>
    </div>
  );
});