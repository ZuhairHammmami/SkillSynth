// File: D:\SkillSynth\src\frontend\components\StepItem.tsx

interface StepItemProps {
  title: string;
  description: string;
  resourceUrl: string;
}

export default function StepItem({ title, description, resourceUrl }: StepItemProps) {
  return (
    <div className="mb-4 rounded-md border p-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-bold">{title}</h4>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
        <button className="rounded-full border px-4 py-1 text-sm">
          لم يتم
        </button>
      </div>
      <a 
        href={resourceUrl} 
        target="_blank" // لفتح الرابط في تبويب جديد
        rel="noopener noreferrer" // ممارسة أمان جيدة عند استخدام target="_blank"
        className="mt-3 inline-block text-blue-600 hover:underline"
      >
        اذهب إلى المصدر
      </a>
    </div>
  );
}