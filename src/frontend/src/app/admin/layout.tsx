// المسار: src/app/admin/layout.tsx
import { AdminGuard } from "@/features/auth/components/AdminGuard";
import { AdminSidebar } from "@/features/admin/components/AdminSidebar";
import { AdminHeader } from "@/features/admin/components/AdminHeader";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AdminGuard>
      <div className="grid min-h-screen w-full lg:grid-cols-[280px_1fr]">
        <AdminSidebar />
        <div className="flex flex-col">
          <AdminHeader />
          <main className="flex-1 p-4 sm:p-6 bg-muted/40">
            {children}
          </main>
        </div>
      </div>
    </AdminGuard>
  );
}