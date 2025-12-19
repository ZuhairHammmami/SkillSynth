// المسار: src/app/components/Header.tsx
'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';
import { Logo } from './Logo';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { LayoutDashboard, LogOut, User as UserIcon, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // قائمة بالصفحات التي لا نريد أن يظهر فيها الهيدر
  const authRoutes = ['/login', '/register', '/forgot-password', '/reset-password'];
  
  // إذا كان المسار الحالي يبدأ بأي من مسارات المصادقة، لا تعرض الهيدر
  if (authRoutes.some(route => pathname.startsWith(route))) {
    return null;
  }

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // دالة آمنة للحصول على الأحرف الأولى من الاسم
  const getInitials = (name: string = ""): string => {
    if (!name) return "U";
    const names = name.trim().split(' ');
    if (names.length > 1 && names[0] && names[names.length - 1]) {
      return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <motion.header 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-background/80 backdrop-blur-sm sticky top-0 z-50 w-full border-b"
    >
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8 py-2 flex justify-between items-center">
        <Link href={isAuthenticated ? "/dashboard" : "/"}>
          <Logo />
        </Link>
        <div className="flex items-center gap-4">
          {isAuthenticated && user ? (
            // حالة المستخدم مسجل دخوله
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                    <Avatar>
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
                <DropdownMenuItem onClick={() => router.push('/dashboard')}>
                    <LayoutDashboard className="mr-2 h-4 w-4" />
                    <span>لوحة التحكم</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/profile')}>
                    <UserIcon className="mr-2 h-4 w-4" />
                    <span>الملف الشخصي</span>
                </DropdownMenuItem>
                {user.is_admin && (
                    <DropdownMenuItem onClick={() => router.push('/admin')}>
                        <ShieldCheck className="mr-2 h-4 w-4" />
                        <span>لوحة تحكم الأدمن</span>
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
            // حالة المستخدم زائر
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