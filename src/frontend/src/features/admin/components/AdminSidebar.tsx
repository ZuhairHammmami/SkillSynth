'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Logo } from '@/components/Logo';
import { useAuthStore } from '@/store/authStore';
import { useLogout } from '@/features/auth/hooks/useLogout';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  LogOut, 
  Database,
  Layers,
  Briefcase,
  BookOpen
} from 'lucide-react';

export function AdminSidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const { mutate: performLogout } = useLogout();

  const sections = [
    {
      title: "الرئيسية",
      items: [
        { title: 'مركز الاستخبارات', href: '/admin/dashboard', icon: LayoutDashboard },
        { title: 'إدارة المستخدمين', href: '/admin/users', icon: Users },
        { title: 'أرشيف المسارات', href: '/admin/paths', icon: FileText },
      ]
    },
    {
      title: "إدارة المحتوى",
      items: [
        { title: 'المهارات (Skills)', href: '/admin/skills', icon: Database },
        { title: 'التصنيفات (Categories)', href: '/admin/categories', icon: Layers },
        { title: 'المصادر (Resources)', href: '/admin/resources', icon: BookOpen },
        { title: 'الأدوار (Job Roles)', href: '/admin/job-roles', icon: Briefcase },
      ]
    }
  ];

  return (
    <div className="hidden lg:flex h-screen w-72 flex-col border-l bg-card/50 backdrop-blur-xl sticky top-0 border-r-0 shadow-sm">
      
      {/* Header */}
      <div className="flex h-[80px] items-center px-6 border-b border-border/50">
        <Link href="/" className="flex items-center gap-3 group w-full">
          <Logo className="w-10 h-10 text-primary transition-transform duration-300 group-hover:scale-110" iconOnly={true} />
          <div className="flex flex-col">
            <span className="font-bold text-xl tracking-tight text-foreground leading-none">SkillSynth</span>
            <span className="text-[10px] font-bold text-primary uppercase tracking-wider bg-primary/10 px-2 py-0.5 rounded-full w-fit mt-1">Admin Panel</span>
          </div>
        </Link>
      </div>

      {/* Body: Navigation */}
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-6">
        {sections.map((section, idx) => (
          <div key={idx}>
            <h3 className="mb-2 px-2 text-xs font-semibold uppercase text-muted-foreground/70 tracking-wider">
              {section.title}
            </h3>
            <nav className="grid gap-1">
              {section.items.map((item, index) => {
                const isActive = pathname === item.href;
                return (
                  <Button
                    key={index}
                    variant={isActive ? 'secondary' : 'ghost'}
                    className={cn(
                      'w-full justify-start gap-3 h-10 font-normal text-sm transition-all',
                      isActive 
                        ? 'bg-primary/10 text-primary font-medium hover:bg-primary/15 translate-x-1' 
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    )}
                    asChild
                  >
                    <Link href={item.href}>
                      <item.icon className={cn("h-4 w-4", isActive ? "text-primary" : "text-muted-foreground/70")} />
                      {item.title}
                    </Link>
                  </Button>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border/50 bg-muted/10">
        <div className="flex items-center gap-3 mb-4 px-2 p-2 rounded-lg bg-card border border-border/50">
            <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-lg shrink-0">
                {user?.full_name?.charAt(0).toUpperCase() || 'A'}
            </div>
            <div className="overflow-hidden flex-1">
                <p className="text-sm font-semibold truncate text-foreground">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground truncate opacity-80">{user?.email}</p>
            </div>
        </div>
        <Button 
            variant="outline" 
            className="w-full justify-start gap-2 text-red-500 hover:text-red-600 border-red-100 hover:bg-red-50"
            onClick={() => performLogout()}
        >
          <LogOut className="h-4 w-4" />
          تسجيل الخروج
        </Button>
      </div>
    </div>
  );
}