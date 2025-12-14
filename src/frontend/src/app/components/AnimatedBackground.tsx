// المسار: src/frontend/src/app/components/AnimatedBackground.tsx
'use client';
import { motion } from 'framer-motion';

export const AnimatedBackground = () => {
  return (
    <div className="absolute inset-0 -z-10 h-full w-full bg-background bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]">
        <motion.div 
            className="absolute inset-0 -z-10 bg-[radial-gradient(circle_500px_at_50%_200px,#3b82f633,transparent)]"
            animate={{
                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
            }}
            transition={{
                duration: 20,
                repeat: Infinity,
                repeatType: "reverse",
            }}
        />
    </div>
  );
};