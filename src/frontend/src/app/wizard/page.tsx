// app/wizard/page.tsx
// سنقوم بإضافة المكونات لاحقًا
export default function WizardPage() {
  return (
    <main className="container mx-auto p-8 flex justify-center">
        <div className="w-full max-w-2xl">
            <h1 className="text-3xl font-bold mb-6 text-center">أنشئ مسارك التعليمي</h1>
            <p className="text-center text-gray-600 mb-8">
                أخبرنا عن هدفك، وسنقوم بتوليد خطة مخصصة لك.
            </p>
            {/* سيتم إضافة مكون GenerateWizard هنا */}
        </div>
    </main>
  );
}