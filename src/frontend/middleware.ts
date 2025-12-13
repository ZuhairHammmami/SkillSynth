// المسار: src/frontend/middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// قائمة بالصفحات التي يجب أن يكون المستخدم مسجلاً دخوله للوصول إليها
const protectedRoutes = ['/dashboard', '/wizard', '/paths'];

// قائمة بصفحات المصادقة (لا يجب أن يصل إليها المستخدم المسجل دخوله)
const authRoutes = ['/login', '/register'];

export function middleware(request: NextRequest) {
  // نحصل على "المفتاح" (التوكن) من الكوكيز
  const token = request.cookies.get('authToken')?.value;
  const { pathname } = request.nextUrl;

  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));
  const isAuthRoute = authRoutes.some(route => pathname.startsWith(route));

  // الحالة 1: المستخدم يحاول الوصول لصفحة محمية وهو غير مسجل دخوله
  if (!token && isProtectedRoute) {
    // أعد توجيهه إلى صفحة تسجيل الدخول
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // الحالة 2: المستخدم مسجل دخوله ويحاول الوصول لصفحة تسجيل الدخول/إنشاء حساب
  if (token && isAuthRoute) {
    // أعد توجيهه إلى لوحة التحكم الخاصة به
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // إذا لم تنطبق أي من الحالات، اسمح له بالمرور
  return NextResponse.next();
}

// تحديد المسارات التي سيتم تطبيق هذا المنطق عليها
export const config = {
  matcher: ['/dashboard/:path*', '/wizard/:path*', '/paths/:path*', '/login', '/register'],
};