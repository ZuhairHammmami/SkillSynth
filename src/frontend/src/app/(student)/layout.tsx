'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { cn } from '@/shared/lib/utils';
import { Logo } from '@/shared/components/Logo';
import { LocaleSwitcher } from '@/shared/components/LocaleSwitcher';
import { LayoutDashboard, Compass, BarChart3, User, Settings, LogOut, Menu, X, ChevronRight } from 'lucide-react';
import { Button } from '@/shared/ui/button';
import { Avatar, AvatarFallback } from '@/shared/ui/avatar';
import { useProfile, useAuth } from '@/shared/hooks/useAuthApi';
import { useRouter } from 'next/navigation';
import { getInitials } from '@/shared/lib/utils';
import { useState } from 'react';

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations('studentLayout');
  const pathname = usePathname();
  const router = useRouter();
  const { data: profile } = useProfile();
  const { logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { href: '/dashboard', label: t('dashboard'), icon: LayoutDashboard },
    { href: '/learn', label: t('myPaths'), icon: Compass },
    { href: '/analytics', label: t('analytics'), icon: BarChart3 },
    { href: '/profile', label: t('profile'), icon: User },
    { href: '/settings', label: t('settings'), icon: Settings },
  ];

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="flex min-h-screen">
      <aside className={cn(
        "fixed inset-y-0 start-0 z-30 w-60 border-e bg-background flex flex-col transition-transform duration-200 lg:translate-x-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        <div className="flex h-14 items-center border-b px-4">
          <Logo href="/dashboard" />
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link key={item.href} href={item.href} className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}>
                <item.icon className="h-4 w-4" />
                {item.label}
                {isActive && <ChevronRight className="ms-auto h-4 w-4" />}
              </Link>
            );
          })}
        </nav>
        <div className="border-t p-3 space-y-3">
          <div className="flex items-center gap-3 px-3">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="text-xs">
                {profile?.full_name ? getInitials(profile.full_name) : profile?.email?.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{profile?.full_name || profile?.email}</p>
              <p className="text-xs text-muted-foreground">{t('dashboard')}</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <LocaleSwitcher />
            <Button variant="ghost" size="sm" onClick={handleLogout} className="gap-2 text-muted-foreground" aria-label={t('logout')}>
              <LogOut className="h-4 w-4" />
              {t('logout')}
            </Button>
          </div>
        </div>
      </aside>

      <div className="flex-1 lg:ps-60">
        <header className="sticky top-0 z-20 flex h-14 items-center gap-4 border-b bg-background px-4 lg:px-6">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <div className="flex-1" />
        </header>
        <main className="p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
