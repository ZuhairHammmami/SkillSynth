// المسار: src/app/components/StepItem.tsx
'use client'; // <-- مهم لأن المكون يستخدم أيقونات

// 1. استيراد المكونات التي نستخدمها من shadcn/ui
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// 2. استيراد الأيقونات التي نستخدمها من lucide-react
import { Check, Link as LinkIcon } from "lucide-react";

// 3. تعريف أنواع البيانات للمدخلات (Props)
type StepItemProps = {
  stepNumber: number;
  title: string;
  resourceTitle: string;
  resourceUrl: string;
};

// 4. المكون نفسه
export default function StepItem({
  stepNumber,
  title,
  resourceTitle,
  resourceUrl,
}: StepItemProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold">
              {stepNumber}
            </div>
            <CardTitle>{title}</CardTitle>
          </div>
          <Button variant="outline" size="icon" title="Mark as complete">
            <Check className="h-4 w-4" />
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