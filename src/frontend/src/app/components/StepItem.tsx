// المسار: src/app/components/StepItem.tsx
'use client';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Check, Link as LinkIcon, Circle } from "lucide-react";

type StepItemProps = {
  stepId: number;
  stepNumber: number;
  title: string;
  resourceTitle: string;
  resourceUrl: string;
  isCompleted: boolean;
  onComplete: (stepId: number) => void;
};

export default function StepItem({
  stepId,
  stepNumber,
  title,
  resourceTitle,
  resourceUrl,
  isCompleted,
  onComplete,
}: StepItemProps) {
  return (
    // نغير شفافية البطاقة إذا كانت مكتملة
    <Card className={`transition-opacity ${isCompleted ? "opacity-60" : "opacity-100"}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div 
              className={`flex h-8 w-8 items-center justify-center rounded-full font-bold transition-colors
              ${isCompleted 
                ? "bg-green-500 text-white" 
                : "bg-primary text-primary-foreground"}`
              }
            >
              {isCompleted ? <Check className="h-5 w-5" /> : stepNumber}
            </div>
            {/* نضيف خطًا على العنوان إذا كانت الخطوة مكتملة */}
            <CardTitle className={isCompleted ? "text-muted-foreground line-through" : ""}>
              {title}
            </CardTitle>
          </div>
          <Button 
            variant={isCompleted ? "secondary" : "outline"} 
            size="sm"
            onClick={() => onComplete(stepId)}
            disabled={isCompleted}
            aria-label={isCompleted ? "الخطوة مكتملة" : "إكمال الخطوة"}
          >
            {isCompleted ? (
              <>
                <Check className="ml-2 h-4 w-4" />
                مكتمل
              </>
            ) : (
              <>
                <Circle className="ml-2 h-4 w-4" />
                إكمال
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <a
          href={resourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors"
        >
          <LinkIcon className="h-4 w-4" />
          <span>{resourceTitle}</span>
        </a>
      </CardContent>
    </Card>
  );
}