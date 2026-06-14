'use client';
import Link from 'next/link';
import { Button } from '@/shared/ui/button';
import { ArrowLeft, Sparkles, Zap, BrainCircuit } from 'lucide-react';
import { useAuthStore } from '@/shared/store/authStore';
import { Logo } from '@/shared/components/Logo';
import { motion } from 'framer-motion';

export default function LandingPage() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <div className="relative isolate pt-14">
      {/* Hero Section */}
      <div className="py-24 sm:py-32 lg:pb-40">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mx-auto max-w-4xl text-center"
          >
            <div className="mb-8 flex justify-center">
                <div className="relative rounded-full px-3 py-1 text-sm leading-6 text-gray-400 ring-1 ring-white/10 hover:ring-white/20 bg-white/5 backdrop-blur-lg">
                    الجيل الجديد من التعلم الذكي <span className="text-purple-400 font-semibold mx-1">AI Powered</span>
                </div>
            </div>
            
            <h1 className="text-5xl font-bold tracking-tight text-white sm:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/50 pb-4">
              لا تدرس بجهد، <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-500">ادرس بذكاء.</span>
            </h1>
            
            <p className="mt-6 text-lg leading-8 text-gray-300 max-w-2xl mx-auto">
              SkillSynth ليس مجرد منصة كورسات. إنه عقلك الثاني الذي يحلل، يخطط، ويرسم لك أقصر طريق لاحتراف مهنة أحلامك.
            </p>
            
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Button asChild size="lg" className="rounded-full h-14 px-8 text-lg bg-white text-black hover:bg-gray-200 shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all hover:scale-105">
                <Link href={isAuthenticated ? "/dashboard" : "/register"}>
                  {isAuthenticated ? "لوحة التحكم" : "ابدأ رحلتك مجانًا"}
                </Link>
              </Button>
              <Link href="/about" className="text-sm font-semibold leading-6 text-white flex items-center hover:text-purple-400 transition-colors">
                كيف نعمل؟ <span aria-hidden="true" className="mr-1">←</span>
              </Link>
            </div>
          </motion.div>

          {/* Cards Section */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mx-auto mt-20 grid max-w-lg grid-cols-1 gap-6 sm:mt-24 lg:max-w-none lg:grid-cols-3"
          >
            {[
                { icon: BrainCircuit, title: "تحليل ذكي", desc: "خوارزميات تفهم مستواك الحالي بدقة وتتجاوز ما تعرفه مسبقاً." },
                { icon: Sparkles, title: "مسار ديناميكي", desc: "لا توجد خطة ثابتة. المسار يتغير ويتطور معك بناءً على سرعة تعلمك." },
                { icon: Zap, title: "تركيز فائق", desc: "نعطيك فقط ما تحتاجه للوظيفة، بدون حشو أو معلومات زائدة." },
            ].map((feature, i) => (
                <div key={i} className="relative overflow-hidden rounded-2xl bg-white/5 p-8 ring-1 ring-white/10 hover:bg-white/10 transition-colors backdrop-blur-sm">
                    <feature.icon className="h-8 w-8 text-purple-400 mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                    <p className="text-gray-400 leading-relaxed">{feature.desc}</p>
                </div>
            ))}
          </motion.div>
        </div>
      </div>
    </div>
  );
}