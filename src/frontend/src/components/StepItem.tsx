'use client';

import { useState } from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, ExternalLink, PlayCircle, FileText, BookOpen, BrainCircuit, Check, X } from 'lucide-react';
import { cn } from "@/lib/utils";
import dynamic from 'next/dynamic';
import { Badge } from './ui/badge';
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { toast } from 'sonner';

// تعريف المشغل
const ReactPlayer = dynamic(() => import('react-player/lazy'), { 
  ssr: false,
  loading: () => <div className="w-full h-full bg-slate-900/50 animate-pulse rounded-xl" />
}) as any;

interface StepProps {
  step: any; 
  index: number;
}

export default function StepItem({ step, index }: StepProps) {
  const [isCompleted, setIsCompleted] = useState(step.is_completed || false);
  const [showQuiz, setShowQuiz] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string>("");
  const [quizStatus, setQuizStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleCompleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isCompleted) {
        // إذا كانت مكتملة ونريد التراجع
        setIsCompleted(false);
        return;
    }

    // إذا كان هناك اختبار ولم يحل بعد
    if (step.assessments && step.assessments.length > 0) {
        setShowQuiz(true);
    } else {
        // لا يوجد اختبار، أكمل مباشرة
        completeStep();
    }
  };

  const completeStep = () => {
      setIsCompleted(true);
      setShowQuiz(false);
      toast.success("أحسنت! تم إكمال الخطوة.");
      // TODO: Call API here
  };

  const submitQuiz = () => {
      // هنا نفترض أن الإجابة الصحيحة هي الخيار الأول كمثال (يجب أن تأتي من الباك اند)
      // في التطبيق الحقيقي سنرسل الإجابة للباك اند للتحقق
      if (selectedAnswer === "0") { 
          setQuizStatus('success');
          setTimeout(completeStep, 1000);
      } else {
          setQuizStatus('error');
          toast.error("إجابة خاطئة، حاول مرة أخرى!");
      }
  };

  const isEmbeddableVideo = (url: string) => {
      return url.includes('youtube.com') || url.includes('youtu.be') || url.includes('vimeo.com');
  };

  return (
    <Accordion type="single" collapsible className="w-full">
      <AccordionItem value={`item-${step.id}`} className="border border-slate-800 rounded-xl bg-slate-900/40 px-4 shadow-sm transition-all hover:border-cyan-500/30 data-[state=open]:border-cyan-500/50 data-[state=open]:bg-slate-900/80">
        
        {/* === رأس الخطوة === */}
        <div className="flex items-center gap-4 py-4">
            <button onClick={handleCompleteClick} className="shrink-0 transition-transform hover:scale-110 focus:outline-none">
                {isCompleted ? (
                    <CheckCircle2 className="w-8 h-8 text-green-500 fill-green-950/20" />
                ) : (
                    <Circle className="w-8 h-8 text-slate-600 hover:text-cyan-400" />
                )}
            </button>

            <AccordionTrigger className="flex-1 hover:no-underline py-0">
                <div className="flex flex-col items-start text-right gap-1 w-full">
                    <div className="flex justify-between w-full">
                        <span className="text-xs font-bold text-cyan-600 uppercase tracking-widest">
                            STEP {index < 10 ? `0${index}` : index}
                        </span>
                        <div className="flex gap-2">
                            {step.resources?.some((r: any) => r.type === 'Video') && 
                                <Badge variant="outline" className="text-[10px] border-blue-500/30 text-blue-400 bg-blue-500/10">VIDEO</Badge>
                            }
                            {step.assessments && step.assessments.length > 0 &&
                                <Badge variant="outline" className="text-[10px] border-yellow-500/30 text-yellow-400 bg-yellow-500/10">QUIZ</Badge>
                            }
                        </div>
                    </div>
                    <span className={cn("text-lg font-bold text-slate-200", isCompleted && "line-through text-slate-600")}>
                        {step.title}
                    </span>
                </div>
            </AccordionTrigger>
        </div>

        {/* === المحتوى === */}
        <AccordionContent className="pt-2 pb-6 pr-12 text-slate-400">
            <div className="space-y-8">
                
                {/* الوصف */}
                <div className="leading-relaxed text-base border-r-2 border-slate-800 pr-4">
                    {step.content || "لا يوجد وصف إضافي."}
                </div>

                {/* المصادر */}
                {step.resources && step.resources.length > 0 && !showQuiz && (
                    <div className="space-y-4">
                        <h4 className="text-sm font-bold flex items-center gap-2 text-white">
                            <BookOpen className="w-4 h-4 text-cyan-500" /> مصادر التعلم
                        </h4>
                        <div className="grid gap-6">
                            {step.resources.map((res: any, idx: number) => (
                                <div key={idx} className="group overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
                                    {res.type === 'Video' && isEmbeddableVideo(res.url) ? (
                                        <div className="aspect-video w-full">
                                            <ReactPlayer url={res.url} width="100%" height="100%" controls />
                                        </div>
                                    ) : (
                                        <a href={res.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-4 p-4 hover:bg-slate-900 transition-colors">
                                            <div className="p-3 rounded-full bg-slate-900 border border-slate-800">
                                                {res.type === 'Article' ? <FileText className="w-5 h-5 text-orange-400" /> : <ExternalLink className="w-5 h-5 text-blue-400" />}
                                            </div>
                                            <div className="flex-1">
                                                <h5 className="font-semibold text-slate-200 group-hover:text-cyan-400 transition-colors">{res.title}</h5>
                                                <p className="text-xs text-slate-500 mt-1">{res.url}</p>
                                            </div>
                                        </a>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* === واجهة الاختبار (تظهر عند محاولة الإكمال) === */}
                {showQuiz && step.assessments && step.assessments.length > 0 && (
                    <div className="bg-slate-950 border border-yellow-500/20 rounded-xl p-6 animate-in fade-in slide-in-from-top-4">
                        <div className="flex items-center gap-3 mb-4 text-yellow-500">
                            <BrainCircuit className="w-6 h-6" />
                            <h4 className="font-bold text-lg">اختبار سريع للفهم</h4>
                        </div>
                        
                        {/* عرض السؤال الأول كمثال */}
                        <div className="space-y-4">
                            <p className="text-white font-medium text-lg">{step.assessments[0].title || "ما هو المفهوم الأساسي في هذا الدرس؟"}</p>
                            
                            <RadioGroup onValueChange={setSelectedAnswer} className="gap-3">
                                {/* خيارات وهمية للعرض (يجب أن تأتي من الـ API) */}
                                {["الخيار الأول الصحيح", "خيار خاطئ 1", "خيار خاطئ 2"].map((opt, i) => (
                                    <div key={i} className={`flex items-center space-x-2 space-x-reverse border rounded-lg p-3 transition-colors ${selectedAnswer === i.toString() ? 'border-cyan-500 bg-cyan-950/20' : 'border-slate-800 hover:bg-slate-900'}`}>
                                        <RadioGroupItem value={i.toString()} id={`opt-${i}`} />
                                        <Label htmlFor={`opt-${i}`} className="flex-1 cursor-pointer text-slate-300">{opt}</Label>
                                    </div>
                                ))}
                            </RadioGroup>

                            <div className="flex gap-3 mt-6">
                                <Button onClick={submitQuiz} className="bg-yellow-600 hover:bg-yellow-500 text-white flex-1">
                                    تحقق من الإجابة
                                </Button>
                                <Button variant="ghost" onClick={() => setShowQuiz(false)}>إلغاء</Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* زر الإكمال الرئيسي */}
                {!showQuiz && (
                    <div className="flex justify-end pt-4 border-t border-slate-800/50">
                        <Button 
                            variant={isCompleted ? "outline" : "default"}
                            onClick={handleCompleteClick}
                            className={cn(
                                "min-w-[140px] transition-all font-bold",
                                isCompleted 
                                    ? "border-green-600 text-green-500 hover:bg-green-950/30 bg-transparent" 
                                    : "bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-900/20"
                            )}
                        >
                            {isCompleted ? "تراجع" : "إتمام الخطوة"}
                        </Button>
                    </div>
                )}
            </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}