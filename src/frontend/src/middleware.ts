import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const learnerRoutes = ['/dashboard', '/wizard', '/paths', '/profile', '/learn', '/analytics', '/settings'];
const authRoutes = ['/login', '/register', '/forgot-password', '/reset-password'];
const supportedLocales = ['en', 'ar'];
const defaultLocale = 'en';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('authToken')?.value;
  const { pathname } = request.nextUrl;

  const isLearnerRoute = learnerRoutes.some(route => pathname === route || pathname.startsWith(route + '/'));
  const isAuthRoute = authRoutes.some(route => pathname === route || pathname.startsWith(route + '/'));

  if (!token && isLearnerRoute) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (token && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  const response = NextResponse.next();

  const localeCookie = request.cookies.get('NEXT_LOCALE')?.value;
  if (!localeCookie || !supportedLocales.includes(localeCookie)) {
    const acceptLanguage = request.headers.get('accept-language') || '';
    let preferredLocale = defaultLocale;
    if (acceptLanguage.startsWith('ar')) {
      preferredLocale = 'ar';
    }
    response.cookies.set('NEXT_LOCALE', preferredLocale, {
      path: '/',
      maxAge: 60 * 60 * 24 * 365,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
    });
  }

  if (token) {
    response.cookies.set('authToken', token, {
      path: '/',
      maxAge: 60 * 60 * 24,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      httpOnly: false,
    });
  }

  return response;
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/wizard/:path*',
    '/paths/:path*',
    '/profile/:path*',
    '/analytics/:path*',
    '/settings/:path*',
    '/learn/:path*',
    '/login',
    '/register',
    '/forgot-password',
    '/reset-password',
  ],
};
