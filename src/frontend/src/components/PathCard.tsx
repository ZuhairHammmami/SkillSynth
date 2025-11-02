// File: D:\SkillSynth\src\frontend\components\PathCard.tsx

// نُعرّف الـ Props التي تحتاجها هذه البطاقة
interface PathCardProps {
  title: string;
  weeklyHours: number;
}

export default function PathCard({ title, weeklyHours }: PathCardProps) {
  return (
    // هذا هو العنصر الرئيسي للبطاقة
    // border, rounded-lg, p-6, shadow-md: تعطي البطاقة شكلاً جميلاً مع حواف دائرية وظل خفيف.
    <div className="rounded-lg border bg-white p-6 shadow-md">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-gray-600">
        الخطة الأسبوعية: {weeklyHours} ساعات
      </p>
      <button className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
        عرض المسار
      </button>
    </div>
  );
}