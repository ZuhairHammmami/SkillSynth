// المسار: src/components/StepItem.tsx
'use client';

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, Link as LinkIcon, Circle, BookOpen, Video, Newspaper } from "lucide-react";
import type { PathStep } from "@/features/paths/hooks/usePathDetails";
import { motion } from 'framer-motion';

interface StepItemProps {
  step: PathStep;
}

const resourceIcons: { [key: string]: React.ReactNode } = {
    'article': <Newspaper className="h-5 w-5 text-sky-500" />,
    'video': <Video className="h-5 w-5 text-red-500" />,
    'book': <BookOpen className="h-5 w-5 text-green-500" />,
    'default': <LinkIcon className="h-5 w-5 text-primary" />,
};

export default function StepItem({ step }: StepItemProps) {
  const isCompleted = false; // مؤقتًا

  return (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.5 }}
    >
      <Accordion type="single" collapsible className="w-full bg-card rounded-lg border shadow-sm">
        <AccordionItem value={`item-${step.id}`} className="border-b-0">
          <AccordionTrigger className="p-6 text-right hover:no-underline w-full">
            {/* =====> هذا هو التصحيح <===== */}
            {/* لقد أزلنا asChild ونضع كل شيء مباشرة داخل Trigger */}
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-4">
                <div className={`flex h-10 w-10 items-center justify-center rounded-full font-bold text-lg transition-colors ${isCompleted ? "bg-green-500 text-white" : "bg-primary text-primary-foreground"}`}>
                  {isCompleted ? <Check size={24} /> : step.step_number}
                </div>
                <h3 className="text-lg font-semibold text-foreground text-left">{step.title}</h3>
              </div>
              <Button 
                variant={isCompleted ? "secondary" : "outline"} 
                size="sm"
                disabled={isCompleted}
                // نمنع الزر من التسبب في فتح/إغلاق الأكورديون
                onClick={(e) => {
                    e.stopPropagation();
                    // يمكنك إضافة منطق onComplete هنا لاحقًا
                }}
              >
                {isCompleted ? 'مكتمل' : 'إكمال'}
              </Button>
            </div>
            {/* ============================== */}
          </AccordionTrigger>
          <AccordionContent className="p-6 pt-0">
            <p className="text-muted-foreground mb-6 border-t pt-4">{step.content}</p>
            {step.resources && step.resources.length > 0 ? (
              <div className="space-y-3">
                <h4 className="font-semibold">الموارد التعليمية المقترحة:</h4>
                {step.resources.map(resource => (
                  <a key={resource.id} href={resource.url} target="_blank" rel="noopener noreferrer" 
                  className="flex items-center gap-4 p-3 rounded-md border bg-muted/50 hover:bg-muted transition-colors">
                    <div>{resourceIcons[resource.type] || resourceIcons['default']}</div>
                    <div className="flex-grow">
                      <p className="font-medium text-foreground">{resource.title}</p>
                      <p className="text-sm text-muted-foreground">{resource.author_or_platform}</p>
                    </div>
                    <div className="text-xs">
                      <Badge variant={resource.is_free ? "default" : "destructive"}>
                        {resource.is_free ? "مجاني" : "مدفوع"}
                      </Badge>
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground italic">لا توجد موارد مقترحة لهذه الخطوة.</p>
            )}
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </motion.div>
  );
}