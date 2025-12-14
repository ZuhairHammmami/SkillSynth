// المسار: src/app/page.tsx
'use client';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Zap, Target, Bot } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Logo } from '@/app/components/Logo';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

const containerVariants = { /* ... */ };
const itemVariants = { /* ... */ };

export default function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <>
      {/* Section 1: Hero */}
      <motion.section
        className="container mx-auto flex flex-col items-center justify-center text-center px-4 pt-20 pb-16 sm:pt-28 sm:pb-24"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants}><Logo /></motion.div>
        
        <motion.h1 
            variants={itemVariants}
            className="mt-6 text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl"
        >
          مسار تعلمك، مُصمم خصيصًا لك.
        </motion.h1>
        
        <motion.p 
            variants={itemVariants}
            className="mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl"
        >
          حوّل أهدافك إلى خطة عمل واضحة وفعالة. SkillSynth يستخدم الذكاء
          الاصطناعي لإنشاء مسار تعليمي مخصص يناسب أسلوبك وجدولك الزمني.
        </motion.p>

        <motion.div variants={itemVariants} className="mt-10">
          <Button asChild size="lg">
            <Link href={isAuthenticated ? "/dashboard" : "/register"}>
              {isAuthenticated ? "اذهب إلى لوحة التحكم" : "ابدأ رحلتك مجانًا"}
              <ArrowLeft className="mr-2 h-5 w-5" />
            </Link>
          </Button>
        </motion.div>
      </motion.section>

      {/* Section 2: Features (Upgraded Design) */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">لماذا تختار SkillSynth؟</h2>
          <div className="grid gap-8 md:grid-cols-3">
            {/* Feature Card 1 */}
            <Card className="text-center">
              <CardHeader>
                <div className="flex items-center justify-center h-12 w-12 rounded-full bg-primary/10 text-primary mx-auto mb-4">
                    <Target className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold">تخصيص ذكي</h3>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">نحلل مستواك وأهدافك لنصمم لك خطة فريدة لا تشبه أي خطة أخرى.</p>
              </CardContent>
            </Card>
            {/* Feature Card 2 */}
            <Card className="text-center">
              <CardHeader>
                <div className="flex items-center justify-center h-12 w-12 rounded-full bg-primary/10 text-primary mx-auto mb-4">
                    <Bot className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold">مدعوم بالذكاء الاصطناعي</h3>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">نظامنا الذكي يختار لك أفضل الموارد ويبقي مسارك محدثًا دائمًا.</p>
              </CardContent>
            </Card>
            {/* Feature Card 3 */}
            <Card className="text-center">
              <CardHeader>
                <div className="flex items-center justify-center h-12 w-12 rounded-full bg-primary/10 text-primary mx-auto mb-4">
                    <Zap className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold">تعلم فعال وموجه</h3>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">لا مزيد من التشتت. اتبع خطوات واضحة وقس تقدمك نحو هدفك بثقة.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Section 3: Testimonials (New) */}
      <section className="bg-muted/50 py-20">
        <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-4">يثق بنا المتعلمون الطموحون</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto mb-12">
                انضم إلى الآلاف الذين حولوا أهدافهم إلى إنجازات حقيقية.
            </p>
            <Card className="max-w-xl mx-auto text-center">
                <CardContent className="pt-6">
                    <p className="text-lg italic">
                        "كان تعلم تطوير الواجهات الأمامية يبدو كجبل لا يمكن تسلقه. SkillSynth أعطاني خارطة طريق واضحة، وفي غضون أسابيع قليلة، كنت أبني مشاريعي الأولى بثقة. إنه مغير لقواعد اللعبة!"
                    </p>
                    <p className="font-semibold mt-6">- سارة أحمد، مطورة واجهة أمامية</p>
                </CardContent>
            </Card>
        </div>
      </section>
    </>
  );
}