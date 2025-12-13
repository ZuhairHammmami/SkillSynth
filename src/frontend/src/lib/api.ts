// المسار: src/frontend/src/lib/api.ts
import axios from 'axios';
import Cookies from 'js-cookie';

const apiClient = axios.create({
  // هذا السطر يقرأ الرابط الأساسي للـ API من ملف متغيرات البيئة
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

/**
 * Interceptor: هذه قطعة كود سحرية تعمل قبل إرسال أي طلب.
 * مهمتها هي التحقق مما إذا كان لدينا "مفتاح" (توكن) في الكوكيز.
 * إذا كان موجودًا، فستضيفه تلقائيًا إلى هيدر Authorization.
 * هذا يعني أننا لن نحتاج إلى كتابة منطق إضافة الهيدر في كل صفحة.
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // في حالة حدوث خطأ أثناء تجهيز الطلب
    return Promise.reject(error);
  }
);

export default apiClient;