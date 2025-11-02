// المسار: src/frontend/src/app/paths/[id]/page.tsx

// 1. استيراد المكونات التي سنستخدمها
// المسار النسبي الصحيح من هذا الملف إلى مجلد المكونات
// المسار الصحيح
import StepItem from '@/app/components/StepItem';

// 2. تعريف أنواع البيانات للمدخلات (Props)
type PageProps = {
  params: { id: string }; // Next.js يمرر الـ id داخل كائن params
};

// 3. بيانات وهمية (مؤقتة) لعرضها في الواجهة
const dummyPathData = {
  title: 'مسار تعلم تطوير الواجهات الأمامية',
  steps: [
    {
      title: 'الخطوة 1: أساسيات HTML',
      description: 'تعلم الهيكل الأساسي لصفحات الويب.',
      resourceUrl: 'https://developer.mozilla.org/ar/docs/Web/HTML',
    },
    {
      title: 'الخطوة 2: تنسيق الصفحات بـ CSS',
      description: 'أضف الألوان والخطوط والتخطيطات لجعل صفحتك جذابة.',
      resourceUrl: 'https://developer.mozilla.org/ar/docs/Web/CSS',
    },
    {
      title: 'الخطوة 3: التفاعلية مع JavaScript',
      description: 'اجعل موقعك يتفاعل مع المستخدم.',
      resourceUrl: 'https://developer.mozilla.org/ar/docs/Web/JavaScript',
    },
  ],
};


// 4. المكون الأساسي للصفحة
export default function PathDetailPage({ params }: PageProps) {
  // `params.id` يحتوي على الرقم أو النص الموجود في رابط المتصفح
  const { id } = params;
  const { title, steps } = dummyPathData;

  return (
    <main className="container mx-auto max-w-4xl p-4 md:p-8">
      {/* قسم العنوان الرئيسي */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-8 border-l-4 border-blue-500">
        <h1 className="text-3xl font-bold text-gray-900">
          {title}
        </h1>
        <p className="text-gray-500 mt-2">
          المعرف الفريد للمسار: {id}
        </p>
      </div>

      {/* قسم خطوات المسار */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800">الخطوات</h2>
        {steps.map((step, index) => (
          <StepItem
            key={index} // مفتاح فريد لكل عنصر في القائمة
            title={step.title}
            description={step.description}
            resourceUrl={step.resourceUrl}
          />
        ))}
      </div>
    </main>
  );
}