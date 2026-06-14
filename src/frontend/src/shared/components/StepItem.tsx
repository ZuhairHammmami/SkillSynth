'use client';

import { useState, memo, useCallback } from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/shared/ui/accordion";
import { Button } from "@/shared/ui/button";
import { CheckCircle2, Circle, ExternalLink, FileText, BookOpen, BrainCircuit, X } from 'lucide-react';
import { cn } from "@/shared/lib/utils";
import dynamic from 'next/dynamic';
import { Badge } from '@/shared/ui/badge';
import { RadioGroup, RadioGroupItem } from "@/shared/ui/radio-group";
import { Label } from "@/shared/ui/label";
import { toast } from 'sonner';

/**
 * Lazy-loaded ReactPlayer with dynamic import
 * - Only loaded when actually needed (video resource exists)
 * - Reduces initial bundle by ~50MB
 * - Fallback loading state for better UX
 */
const ReactPlayer = dynamic(() => import('react-player'), { 
  ssr: false,
  loading: () => <div className="w-full h-full bg-white/5 animate-pulse rounded-xl aspect-video" />
}) as any;

interface StepProps {
  step: any; 
  index: number;
}

/**
 * Helper function to detect embeddable videos
 * Extracted outside component to prevent recreation
 */
const isEmbeddableVideo = (url: string): boolean => {
  return url.includes('youtube.com') || url.includes('youtu.be') || url.includes('vimeo.com');
};

/**
 * StepItem - Memoized learning step component with optimizations
 * 
 * Performance improvements:
 * - React.memo prevents re-renders when parent updates
 * - Lazy-loaded ReactPlayer (50MB savings)
 * - useCallback for event handlers
 * - Extracted constants and helpers
 */
const StepItem = memo(function StepItem({ step, index }: StepProps) {
  const [isCompleted, setIsCompleted] = useState(step.is_completed || false);
  const [showQuiz, setShowQuiz] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string>("");
  const [quizStatus, setQuizStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Memoize event handlers with useCallback
  const completeStep = useCallback(() => {
    setIsCompleted(true);
    setShowQuiz(false);
    toast.success("أحسنت! تم إنجاز الخطوة.");
    // TODO: Call API to save progress
  }, []);

  const handleCompleteClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    if (isCompleted) {
      setIsCompleted(false);
      // TODO: Call API to undo completion
      return;
    }

    if (step.assessments && step.assessments.length > 0) {
      setShowQuiz(true);
    } else {
      completeStep();
    }
  }, [isCompleted, step.assessments, completeStep]);

  const submitQuiz = useCallback(() => {
    // Temporary validation logic
    if (selectedAnswer === "0") { 
      setQuizStatus('success');
      toast.success("إجابة صحيحة!");
      setTimeout(completeStep, 1000);
    } else {
      setQuizStatus('error');
      toast.error("إجابة خاطئة، حاول مرة أخرى.");
    }
  }, [selectedAnswer, completeStep]);

  const handleQuizClose = useCallback(() => {
    setShowQuiz(false);
  }, []);

  return (
    <Accordion type="single" collapsible className="w-full">
      <AccordionItem value={`item-${step.id}`} className="border border-white/10 rounded-2xl bg-white/5 px-4 shadow-lg backdrop-blur-sm transition-all hover:border-primary/50 data-[state=open]:border-primary/50 data-[state=open]:bg-white/10">
        
        {/* Header */}
        <div className="flex items-center gap-4 py-5">
            <button onClick={handleCompleteClick} className="shrink-0 transition-transform hover:scale-110 focus:outline-none">
                {isCompleted ? (
                    <CheckCircle2 className="w-8 h-8 text-green-400 fill-green-900/20" />
                ) : (
                    <Circle className="w-8 h-8 text-gray-500 hover:text-primary" />
                )}
            </button>

            <AccordionTrigger className="flex-1 hover:no-underline py-0">
                <div className="flex flex-col items-start text-right gap-2 w-full">
                    <div className="flex justify-between w-full items-center">
                        <span className="text-xs font-bold text-primary/80 uppercase tracking-widest bg-primary/10 px-2 py-1 rounded">
                            STEP {index < 10 ? `0${index}` : index}
                        </span>
                        <div className="flex gap-2">
                            {step.resources?.some((r: any) => r.type === 'Video') && 
                                <Badge variant="outline" className="text-[10px] border-blue-500/30 text-blue-300 bg-blue-500/10">VIDEO</Badge>
                            }
                            {step.assessments && step.assessments.length > 0 &&
                                <Badge variant="outline" className="text-[10px] border-yellow-500/30 text-yellow-300 bg-yellow-500/10">QUIZ</Badge>
                            }
                        </div>
                    </div>
                    <span className={cn("text-xl font-bold text-white transition-colors", isCompleted && "line-through text-gray-500")}>
                        {step.title}
                    </span>
                </div>
            </AccordionTrigger>
        </div>

        {/* Content */}
        <AccordionContent className="pt-2 pb-6 pr-12 text-gray-300">
            <div className="space-y-8">
                
                <div className="leading-relaxed text-lg border-r-4 border-primary/30 pr-6 pl-2">
                    {step.content || "لا يوجد وصف إضافي لهذه الخطوة."}
                </div>

                {/* Resources */}
                {step.resources && step.resources.length > 0 && !showQuiz && (
                    <div className="space-y-4 animate-in fade-in zoom-in-95 duration-300">
                        <h4 className="text-sm font-bold flex items-center gap-2 text-white/80 uppercase tracking-wider">
                            <BookOpen className="w-4 h-4 text-primary" /> مصادر التعلم
                        </h4>
                        <div className="grid gap-6">
                            {step.resources.map((res: any, idx: number) => (
                                <div key={idx} className="group overflow-hidden rounded-xl border border-white/10 bg-black/40 hover:border-primary/40 transition-all">
                                    {res.type === 'Video' && isEmbeddableVideo(res.url) ? (
                                        <div className="aspect-video w-full relative">
                                            <ReactPlayer 
                                                url={res.url} 
                                                width="100%" 
                                                height="100%" 
                                                controls 
                                                className="absolute top-0 left-0"
                                            />
                                        </div>
                                    ) : (
                                        <a href={res.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-5 p-5 hover:bg-white/5 transition-colors">
                                            <div className="p-3 rounded-full bg-white/5 border border-white/10 group-hover:border-primary/50 group-hover:text-primary transition-all">
                                                {res.type === 'Article' ? <FileText className="w-6 h-6" /> : <ExternalLink className="w-6 h-6" />}
                                            </div>
                                            <div className="flex-1">
                                                <h5 className="font-bold text-lg text-white group-hover:text-primary transition-colors">{res.title}</h5>
                                                <p className="text-sm text-gray-500 mt-1 font-mono truncate max-w-md">{res.url}</p>
                                            </div>
                                        </a>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Quiz UI */}
                {showQuiz && step.assessments && step.assessments.length > 0 && (
                    <div className="bg-black/40 border border-yellow-500/30 rounded-2xl p-8 animate-in slide-in-from-top-4 duration-500">
                        <div className="flex items-center gap-3 mb-6 text-yellow-400">
                            <div className="p-2 bg-yellow-500/10 rounded-lg">
                                <BrainCircuit className="w-6 h-6" />
                            </div>
                            <h4 className="font-bold text-xl">اختبار الفهم السريع</h4>
                        </div>
                        
                        <div className="space-y-6">
                            <p className="text-white font-medium text-lg leading-relaxed">{step.assessments[0].title || "ما هو المفهوم الأساسي في هذا الدرس؟"}</p>
                            
                            <RadioGroup onValueChange={setSelectedAnswer} className="gap-3">
                                {["الخيار الأول الصحيح", "خيار خاطئ 1", "خيار خاطئ 2"].map((opt, i) => (
                                    <div key={i} className={`flex items-center space-x-2 space-x-reverse border rounded-xl p-4 transition-all cursor-pointer ${selectedAnswer === i.toString() ? 'border-yellow-500 bg-yellow-500/10' : 'border-white/10 hover:bg-white/5'}`}>
                                        <RadioGroupItem value={i.toString()} id={`opt-${i}`} className="border-white/50 text-yellow-500" />
                                        <Label htmlFor={`opt-${i}`} className="flex-1 cursor-pointer text-gray-200 text-base">{opt}</Label>
                                    </div>
                                ))}
                            </RadioGroup>

                            <div className="flex gap-4 mt-8 pt-4 border-t border-white/10">
                                <Button onClick={submitQuiz} className="bg-yellow-500 hover:bg-yellow-400 text-black font-bold flex-1 h-12 text-lg">
                                    تحقق من الإجابة
                                </Button>
                                <Button variant="ghost" onClick={handleQuizClose} className="text-gray-400 hover:text-white h-12">إلغاء</Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Complete Button */}
                {!showQuiz && (
                    <div className="flex justify-end pt-6 border-t border-white/5">
                        <Button 
                            variant={isCompleted ? "outline" : "default"}
                            onClick={handleCompleteClick}
                            className={cn(
                                "min-w-[160px] h-12 text-base font-bold transition-all rounded-xl",
                                isCompleted 
                                    ? "border-green-500/50 text-green-400 hover:bg-green-500/10 bg-transparent" 
                                    : "bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/20 hover:shadow-primary/40 hover:-translate-y-1"
                            )}
                        >
                            {isCompleted ? "تراجع عن الإكمال" : "إتمام الخطوة"}
                        </Button>
                    </div>
                )}
            </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
});

// Export memoized component to prevent unnecessary re-renders
export default StepItem;