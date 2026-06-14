// المسار: src/lib/api.ts
import axios from 'axios';
import Cookies from 'js-cookie';

/**
 * ننشئ "instance" من axios مع إعدادات أساسية.
 * - baseURL: هذا هو الجزء الثابت من كل طلباتنا. سيتم جلبه من متغيرات البيئة.
 *            هذا يسمح لنا بتغيير رابط الـ API بسهولة بين بيئة التطوير والإنتاج.
 */
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

/**
 * هنا يكمن السحر. نستخدم "معترض الطلبات" (request interceptor).
 * هذه الدالة سيتم استدعاؤها تلقائيًا **قبل** إرسال أي طلب باستخدام `apiClient`.
 */
apiClient.interceptors.request.use(
  (config) => {
    // 1. نحاول قراءة التوكن من الكوكيز.
    const token = Cookies.get('authToken');
    
    // 2. إذا وجدنا توكن، نقوم بإضافته إلى هيدر 'Authorization'.
    //    هذا يضمن أن كل الطلبات المحمية سيتم مصادقتها تلقائيًا.
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 3. نعيد الإعدادات (config) المعدلة ليكمل الطلب طريقه.
    return config;
  },
  (error) => {
    // في حالة حدوث خطأ أثناء إعداد الطلب، نرفضه.
    return Promise.reject(error);
  }
);

export default apiClient;