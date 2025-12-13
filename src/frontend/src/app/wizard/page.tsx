import GenerateWizard from "@/app/components/GenerateWizard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function WizardPage() {
  return (
    <div className="container mx-auto flex justify-center py-16 px-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl">أنشئ مسارك التعليمي</CardTitle>
          <CardDescription className="pt-2">أخبرنا عن هدفك، وسنقوم بتوليد خطة مخصصة لك مدعومة بالذكاء الاصطناعي.</CardDescription>
        </CardHeader>
        <CardContent>
          <GenerateWizard />
        </CardContent>
      </Card>
    </div>
  );
}
