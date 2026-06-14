// المسار: src/components/AppLayout.tsx
'use client';
import { usePathname } from 'next/navigation';
import Header from '@/shared/components/Header';
import { AnimatedBackground } from '@/shared/components/AnimatedBackground';

export function AppLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const isAuthOrAdminRoute = pathname.startsWith('/login') || 
                               pathname.startsWith('/register') || 
                               pathname.startsWith('/forgot-password') || 
                               pathname.startsWith('/reset-password') || 
                               pathname.startsWith('/admin');

    if (isAuthOrAdminRoute) {
        return <>{children}</>;
    }

    return (
        <div className="relative flex min-h-screen flex-col">
            <AnimatedBackground />
            <Header />
            <main className="flex-grow z-10">{children}</main>
        </div>
    );
}