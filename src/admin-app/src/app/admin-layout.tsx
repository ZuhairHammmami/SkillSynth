'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Logo } from './logo';
import { useAuth } from '@/lib/auth';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { getInitials } from '@/lib/utils';
import { useState } from 'react';
import {
  LayoutDashboard, Users, BookOpen, FileText, ClipboardCheck,
  Compass, BarChart3, HeartPulse, Settings, ScrollText, LogOut,
  Menu, X, ChevronRight, Database, HardDrive, ToggleLeft,
  FolderTree, Briefcase,
} from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/users', label: 'Users', icon: Users },
  { href: '/categories', label: 'Categories', icon: FolderTree },
  { href: '/skills', label: 'Skills', icon: BookOpen },
  { href: '/resources', label: 'Resources', icon: FileText },
  { href: '/job-roles', label: 'Job Roles', icon: Briefcase },
  { href: '/assessments', label: 'Assessments', icon: ClipboardCheck },
  { href: '/paths', label: 'Paths', icon: Compass },
  { href: '/reports', label: 'Reports', icon: BarChart3 },
  { href: '/health', label: 'System Health', icon: HeartPulse },
  { href: '/settings', label: 'Settings', icon: Settings },
  { href: '/audit-logs', label: 'Audit Logs', icon: ScrollText },
  { href: '/backups', label: 'Backups', icon: HardDrive },
  { href: '/db-inspector', label: 'DB Inspector', icon: Database },
  { href: '/feature-flags', label: 'System Configuration', icon: ToggleLeft },
];

export function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { profile, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <div className="flex min-h-screen">
      <aside className={cn(
        "fixed inset-y-0 start-0 z-30 w-60 border-e bg-background flex flex-col transition-transform duration-200 lg:translate-x-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        <div className="flex h-14 items-center border-b px-4">
          <Logo />
          <span className="ms-2 rounded-md bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-600">Admin</span>
        </div>
        <div className="border-t-2 border-amber-500 mx-3" />
        <nav className="flex-1 overflow-y-auto space-y-1 p-3">
          {navItems.map((item) => {
            const isActive = item.href === '/dashboard'
              ? pathname === '/dashboard'
              : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
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
              <p className="text-xs text-muted-foreground">Admin</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={handleLogout} className="w-full gap-2 text-muted-foreground justify-start">
            <LogOut className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </aside>

      <div className="flex-1 lg:ps-60">
        <header className="sticky top-0 z-20 flex h-14 items-center gap-4 border-b bg-background px-4 lg:px-6">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <div className="flex-1" />
        </header>
        <main className="p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
