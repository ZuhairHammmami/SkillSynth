// المسار: src/frontend/src/app/components/Logo.tsx
import React from 'react';

export const Logo = () => (
  <div className="flex items-center gap-2">
    <svg 
      width="28" 
      height="28" 
      viewBox="0 0 24 24" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className="text-primary"
    >
      <path 
        d="M17 6.5C17 4.01472 14.9853 2 12.5 2C10.0147 2 8 4.01472 8 6.5C8 8.98528 10.0147 11 12.5 11H16" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      />
      <path 
        d="M8 17.5C8 19.9853 10.0147 22 12.5 22C14.9853 22 17 19.9853 17 17.5C17 15.0147 14.9853 13 12.5 13H8" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      />
    </svg>
    <span className="font-bold text-xl text-foreground">SkillSynth</span>
  </div>
);