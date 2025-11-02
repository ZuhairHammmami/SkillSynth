// app/components/GenerateWizard.tsx
'use client';

import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

// تعريف أنواع البيانات
interface GeneratePathPayload {
  goal: string;
  weekly_hours: number;
  preferences: { [key: string]: any };
}

interface GeneratePathResponse {
  path_id: string;
  // أضف أي بيانات أخرى تأتي من الـ API
}

export default function GenerateWizard() {
  const router = useRouter();
  
  // States للنموذج
  const [goal, setGoal] = useState('');
  const [hours, setHours] = useState(10);
  const [preferences, setPreferences] = useState('');

  // States لحالة الـ API
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const payload: GeneratePathPayload = {
      goal,
      weekly_hours: hours,
      preferences: {
        tags: preferences.split(',').map(tag => tag.trim()).filter(tag => tag),
      },
    };

    try {
      // استدعاء الـ API
      const response = await axios.post<GeneratePathResponse>(
        '${process.env.NEXT_PUBLIC_API_BASE_URL}', // هذا مسار وهمي، سيتم استبداله
        payload
      );
      
      console.log('API Response:', response.data);

      // بعد النجاح، انتقل إلى صفحة المسار
      router.push(`/paths/${response.data.path_id}`);

    } catch (err) {
      console.error('API Error:', err);
      setError('حدث خطأ أثناء إنشاء المسار. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-8 bg-white rounded-lg shadow-lg space-y-6">
      {/* ... حقول النموذج كما هي ... */}
        <div>
            <label htmlFor="goal" className="block text-sm font-medium text-gray-700">
              ما هو هدفك التعليمي؟ (مثال: تعلم تطوير الواجهات الأمامية)
            </label>
            <textarea
              id="goal"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              rows={3}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
              required
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="hours" className="block text-sm font-medium text-gray-700">
              كم ساعة يمكنك تخصيصها أسبوعيًا؟
            </label>
            <input
              id="hours"
              type="number"
              value={hours}
              onChange={(e) => setHours(Number(e.target.value))}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
              required
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="preferences" className="block text-sm font-medium text-gray-700">
              ما هي تفضيلاتك؟ (فيديو، مقالات، مشاريع عملية - افصل بينها بفاصلة)
            </label>
            <input
              id="preferences"
              type="text"
              value={preferences}
              onChange={(e) => setPreferences(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
              disabled={isLoading}
            />
          </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        type="submit"
        className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        disabled={isLoading}
      >
        {isLoading ? 'جارٍ التوليد...' : 'ولّد المسار'}
      </button>
    </form>
  );
  
}