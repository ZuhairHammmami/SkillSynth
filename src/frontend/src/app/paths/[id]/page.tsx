'use client';

import { useParams, notFound } from 'next/navigation';
import { usePathDetails } from '@/features/paths/hooks/usePathDetails';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import StepItem from '@/shared/components/StepItem';
import { Badge } from "@/shared/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/shared/ui/alert";
import { Terminal, AlertCircle, Clock, CheckCircle2, Share2 } from 'lucide-react';
import { Skeleton } from '@/shared/ui/skeleton';
import { motion } from 'framer-motion';
import { Progress } from "@/shared/ui/progress";
import { Button } from '@/shared/ui/button';

function PathDetailContent() {
  const params = useParams();
  const pathId = params.id as string;
  const { data: pathDetails, isLoading, isError } = usePathDetails(pathId);

  if (isLoading) return <PathSkeleton />;
  
  if (isError) {
    return (
        <Alert variant="destructive" className="max-w-2xl mx-auto mt-20 border-red-900 bg-red-950/50 text-red-200">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>انقطع الاتصال</AlertTitle>
            <AlertDescription>لم نتمكن من تحميل المسار. تحقق من اتصالك وحاول مجدداً.</AlertDescription>
        </Alert>
    );
  }

  if (!pathDetails) return notFound();

  // حساب التقدم (آمن حتى لو كانت البيانات ناقصة)
  const steps = pathDetails.steps || [];
  const completedSteps = steps.filter(s => s.is_completed).length;
  const totalSteps = steps.length;
  const progressPercentage = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
      className="space-y-12"
    >
      {/* === Hero Section: رأس الصفحة === */}
      <div className="relative overflow-hidden rounded-3xl bg-slate-900/50 border border-slate-800 p-8 md:p-12 text-center shadow-2xl backdrop-blur-sm">
        {/* خلفية جمالية داخل البطاقة */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1/2 bg-gradient-to-b from-cyan-500/10 to-transparent blur-3xl pointer-events-none" />
        
        <motion.div 
            initial={{ y: 20, opacity: 0 }} 
            animate={{ y: 0, opacity: 1 }} 
            transition={{ delay: 0.2 }}
        >
            {/* المهارات (Tags) */}
            {pathDetails.skills && (
                <div className="flex justify-center flex-wrap gap-2 mb-6">
                {pathDetails.skills.map(skill => (
                    <Badge key={skill.id} variant="secondary" className="bg-slate-800 text-cyan-400 hover:bg-slate-700 border-slate-700">
                        {skill.name}
                    </Badge>
                ))}
                </div>
            )}

            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
                {pathDetails.title}
            </h1>
            <p className="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed">
                {pathDetails.description}
            </p>

            {/* شريط المعلومات */}
            <div className="flex flex-wrap justify-center items-center gap-6 mt-8">
                <div className="flex items-center gap-2 text-slate-300 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700">
                    <Clock className="w-5 h-5 text-cyan-500" />
                    <span className="font-mono font-bold">{pathDetails.total_estimated_hours || 'غير محدد'} ساعة</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    <span className="font-mono font-bold">{completedSteps}/{totalSteps} خطوات</span>
                </div>
                {/* زر مشاركة (شكلي) */}
                <Button variant="ghost" size="icon" className="text-slate-400 hover:text-white hover:bg-slate-800 rounded-full">
                    <Share2 className="w-5 h-5" />
                </Button>
            </div>
        </motion.div>
      </div>

      {/* === Progress Bar === */}
      <div className="sticky top-20 z-40 bg-slate-950/80 backdrop-blur-md py-4 border-b border-slate-800">
          <div className="container max-w-4xl mx-auto flex items-center gap-4">
              <span className="text-sm font-semibold text-cyan-500 whitespace-nowrap">{Math.round(progressPercentage)}% مكتمل</span>
              <Progress value={progressPercentage} className="h-2 bg-slate-800" indicatorClassName="bg-gradient-to-r from-cyan-500 to-blue-600" />
          </div>
      </div>
      
      {/* === Steps List === */}
      <div className="max-w-4xl mx-auto space-y-6">
        {steps.length > 0 ? (
          steps.map((step, index) => (
            <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
            >
                <StepItem step={step} index={index + 1} />
            </motion.div>
          ))
        ) : (
          <div className="text-center py-20 border border-dashed border-slate-800 rounded-2xl bg-slate-900/30">
            <Terminal className="h-12 w-12 mx-auto text-slate-600 mb-4" />
            <h3 className="text-xl font-bold text-slate-300">المسار قيد التجهيز</h3>
            <p className="text-slate-500 mt-2">يقوم الذكاء الاصطناعي ببناء الخطوات... يرجى الانتظار قليلاً.</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function PathSkeleton() {
    return (
        <div className="space-y-8 mt-10">
            <Skeleton className="h-80 w-full rounded-3xl bg-slate-800/50" />
            <div className="max-w-4xl mx-auto space-y-4">
                <Skeleton className="h-24 w-full rounded-xl bg-slate-800/50" />
                <Skeleton className="h-24 w-full rounded-xl bg-slate-800/50" />
                <Skeleton className="h-24 w-full rounded-xl bg-slate-800/50" />
            </div>
        </div>
    );
}

export default function PathDetailPage() {
    return (
        <AuthGuard>
            <main className="container mx-auto p-4 sm:p-6 pb-20">
                <PathDetailContent />
            </main>
        </AuthGuard>
    );
}