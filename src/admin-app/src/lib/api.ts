import axios from 'axios';
import Cookies from 'js-cookie';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
});

apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get('adminToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      Cookies.remove('adminToken');
      if (typeof window !== 'undefined') {
        window.location.href = '/';
      }
    }
    if (error.response?.data?.detail && !error.response?.data?.__normalized) {
      const detail = error.response.data.detail;
      if (Array.isArray(detail)) {
        error.response.data.detail = detail
          .map((e: unknown) => (typeof e === 'object' && e ? (e as Record<string, unknown>).msg ?? String(e) : String(e)))
          .join('; ');
      }
      error.response.data.__normalized = true;
    }
    return Promise.reject(error);
  }
);

export default apiClient;
