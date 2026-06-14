// src/features/admin/components/AdminHeader.tsx
'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/shared/ui/button';
import { useUser } from '@/features/user/hooks/useUser';
import { useLogout } from '@/features/auth/hooks/useLogout';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/shared/ui/avatar";
import { LogOut, User as UserIcon, Eye } from 'lucide-react';

export function AdminHeader() {
  // User data from React Query
  const { user, isLoading } = useUser();
  const { mutate: performLogout } = useLogout();
  const router = useRouter();

  // Safe utility to get initials from name
  const getInitials = (name: string = ""): string => {
    if (!name) return "AD"; // Admin
    const names = name.trim().split(' ');
    if (names.length > 1 && names[0] && names[names.length - 1]) {
      return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
    }
    if (name.length > 1) {
        return name.substring(0, 2).toUpperCase();
    }
    return name.toUpperCase();
  };

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-6">
        <div className="flex-1">
            {/* Breadcrumbs or page title can go here */}
        </div>
        <div className="ml-auto flex items-center gap-4">
            <Button variant="outline" size="sm" onClick={() => router.push('/dashboard')}>
                <Eye className="h-4 w-4 ml-2" />
                عرض كـ مستخدم
            </Button>
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                        <Avatar className="h-10 w-10">
                            <AvatarFallback>{getInitials(user?.full_name)}</AvatarFallback>
                        </Avatar>
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                    <DropdownMenuLabel className="font-normal">
                        <div className="flex flex-col space-y-1">
                            <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                            <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                        </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => router.push('/profile')}>
                        <UserIcon className="mr-2 h-4 w-4" />
                        <span>الملف الشخصي</span>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => performLogout()} className="text-destructive">
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>تسجيل الخروج</span>
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </div>
    </header>
  );
}