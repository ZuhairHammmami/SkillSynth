// المسار: src/frontend/src/app/wizard/page.tsx

// استيراد المكون الذي يحتوي على النموذج
import GenerateWizard from "@/app/components/GenerateWizard";

export default function WizardPage() {
  return (
    <div className="container mx-auto max-w-2xl px-4 py-16">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-primary">أنشئ مسارك التعليمي</h1>
        <p className="mt-4 text-lg text-muted-foreground">
          أخبرنا عن هدفك، وسنقوم بتوليد خطة مخصصة لك.
        </p>
      </div>
      
      {/* هنا نضع النموذج الذي قمنا بتصميمه سابقًا */}
      <GenerateWizard />
    </div>
  );
}