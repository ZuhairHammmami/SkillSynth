// المسار: src/app/page.tsx
'use client';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Zap, Target, Bot } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { Logo } from '@/components/Logo';
import { motion, Variants } from 'framer-motion'; // <-- 1. استيراد Variants
import { Card, CardContent, CardHeader } from '@/components/ui/card';

// 2. التعريف الصريح للأنواع
const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
    },
  },
};

const itemVariants: Variants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.6,
      ease: "easeOut",
    },
  },
};

export default function LandingPage() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <>
      {/* --- Hero Section --- */}
      <motion.section
        className="container mx-auto flex flex-col items-center justify-center text-center px-4 pt-32 pb-20 sm:pt-40 sm:pb-28"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}><Logo /></motion.div>
        
        <motion.h1 
            variants={itemVariants}
            className="mt-6 text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary via-blue-600 to-secondary sm:text-6xl md:text-7xl"
        >
          مسار تعلمك، مُعاد تصوره.
        </motion.h1>
        
        <motion.p 
            variants={itemVariants}
            className="mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl"
        >
          توقف عن التخمين، وابدأ في الإنجاز. SkillSynth هو شريكك الذكي الذي يحول
          طموحاتك الكبيرة إلى خطوات يومية قابلة للتنفيذ.
        </motion.p>

        <motion.div 
          variants={itemVariants} 
          className="mt-10"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Button asChild size="lg" className="px-8 py-6 text-lg">
            <Link href={isAuthenticated ? "/dashboard" : "/register"}>
              {isAuthenticated ? "اذهب إلى لوحة التحكم" : "ابدأ رحلتك مجانًا"}
              <ArrowLeft className="mr-2 h-5 w-5" />
            </Link>
          </Button>
        </motion.div>
      </motion.section>

      {/* --- Features Section --- */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.h2 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, amount: 0.5 }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-bold text-center mb-12"
          >
              القوة بين يديك
          </motion.h2>
          <div className="grid gap-8 md:grid-cols-3">
            {[
              { icon: Target, title: "تخصيص فائق", desc: "نحلل مستواك وأهدافك لنصمم لك خطة فريدة لا تشبه أي خطة أخرى." },
              { icon: Bot, title: "ذكاء اصطناعي متقدم", desc: "نظامنا الذكي يختار لك أفضل الموارد ويبقي مسارك محدثًا دائمًا." },
              { icon: Zap, title: "تقدم متسارع", desc: "لا مزيد من التشتت. اتبع خطوات واضحة وقس تقدمك نحو هدفك بثقة." },
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.5 }}
                transition={{ duration: 0.5, delay: i * 0.2 }}
              >
                <Card className="text-center h-full transition-all duration-300 hover:border-primary hover:shadow-2xl hover:-translate-y-2">
                  <CardHeader>
                    <div className="flex items-center justify-center h-14 w-14 rounded-full bg-primary/10 text-primary mx-auto mb-4">
                      <feature.icon className="h-7 w-7" />
                    </div>
                    <h3 className="text-xl font-semibold">{feature.title}</h3>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{feature.desc}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}