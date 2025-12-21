'use client';

export const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 -z-50 overflow-hidden pointer-events-none">
      {/* Blob 1: Purple/Indigo */}
      <div 
        className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"
        style={{ backgroundColor: '#6366f1' }} // Indigo
      ></div>
      
      {/* Blob 2: Cyan/Blue */}
      <div 
        className="absolute top-[20%] left-[-10%] w-[400px] h-[400px] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"
        style={{ backgroundColor: '#06b6d4' }} // Cyan
      ></div>
      
      {/* Blob 3: Pink/Rose */}
      <div 
        className="absolute bottom-[-10%] left-[20%] w-[600px] h-[600px] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"
        style={{ backgroundColor: '#f43f5e' }} // Rose
      ></div>
      
      {/* Grid Pattern Overlay (اختياري ليعطي مظهر تقني) */}
      <div className="absolute inset-0 bg-grid-slate-900/[0.02] [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-400/[0.05]"></div>
    </div>
  );
};