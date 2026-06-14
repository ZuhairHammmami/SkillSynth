// src/shared/components/Header.tsx
'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { memo, useMemo, useCallback } from 'react';
import { Button } from '@/shared/ui/button';
import { useAuthStore } from '@/shared/store/authStore';
import { useUser } from '@/features/user/hooks/useUser';
import { useLogout } from '@/features/auth/hooks/useLogout';
import { Logo } from './Logo';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/shared/ui/avatar";
import { LayoutDashboard, LogOut, User as UserIcon, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';

// Memoized constants to prevent recreation on each render
const HIDDEN_ROUTES = ['/login', '/register', '/forgot-password', '/reset-password', '/admin'];

const getInitials = (name: string = ""): string => {
  if (!name) return "U";
  const names = name.trim().split(' ');
  if (names.length > 1 && names[0] && names[names.length - 1]) {
    return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
  }
  if (name.length > 1) {
    return name.substring(0, 2).toUpperCase();
  }
  return name.toUpperCase();
};

function HeaderContent() {
  // Session state from Zustand (auth status, loading)
  const { isAuthenticated } = useAuthStore();
  
  // User data from React Query (profile information)
  const { user, isLoading } = useUser();
  
  const { mutate: performLogout } = useLogout();
  const router = useRouter();
  const pathname = usePathname();

  // Memoize dashboard URL calculation
  const dashboardUrl = useMemo(
    () => user?.is_admin ? '/admin/dashboard' : '/dashboard',
    [user?.is_admin]
  );

  // Memoize navigation handlers
  const handleNavigateToDashboard = useCallback(() => {
    router.push(dashboardUrl);
  }, [router, dashboardUrl]);

  const handleNavigateToProfile = useCallback(() => {
    router.push('/profile');
  }, [router]);

  const handleNavigateToAdmin = useCallback(() => {
    router.push('/admin/dashboard');
  }, [router]);

  const handleLogout = useCallback(() => {
    performLogout();
  }, [performLogout]);

  // Check if header should be hidden
  const shouldHideHeader = useMemo(
    () => HIDDEN_ROUTES.some(route => pathname.startsWith(route)),
    [pathname]
  );
  
  if (shouldHideHeader) {
    return null;
  }

  return (
    <motion.header 
     className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-black/20 backdrop-blur-md supports-[backdrop-filter]:bg-black/10"
    >
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8 py-2 flex justify-between items-center">
        <Link href={isAuthenticated ? dashboardUrl : "/"}>
          <Logo />
        </Link>
        <div className="flex items-center gap-4">
          {isAuthenticated && user && !isLoading ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback>{getInitials(user.full_name)}</AvatarFallback>
                    </Avatar>
                  </Button>
                </motion.div>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user.full_name}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleNavigateToDashboard}>
                    <LayoutDashboard className="mr-2 h-4 w-4" />
                    <span>لوحة التحكم</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleNavigateToProfile}>
                    <UserIcon className="mr-2 h-4 w-4" />
                    <span>الملف الشخصي</span>
                </DropdownMenuItem>
                {user.is_admin && (
                    <DropdownMenuItem onClick={handleNavigateToAdmin}>
                        <ShieldCheck className="mr-2 h-4 w-4" />
                        <span>إدارة النظام</span>
                    </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:bg-destructive/10 focus:text-destructive">
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>تسجيل الخروج</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex items-center gap-2">
                <Button asChild variant="ghost">
                    <Link href="/login">تسجيل الدخول</Link>
                </Button>
                <Button asChild>
                    <Link href="/register">أنشئ حسابًا</Link>
                </Button>
            </div>
          )}
        </div>
      </nav>
    </motion.header>
  );
}

// Export memoized Header to prevent unnecessary re-renders
export default memo(HeaderContent);