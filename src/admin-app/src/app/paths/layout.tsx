import { AdminLayout } from '@/app/admin-layout';
import { AdminGuard } from '@/components/AdminGuard';

export default function PathsLayout({ children }: { children: React.ReactNode }) {
  return <AdminGuard><AdminLayout>{children}</AdminLayout></AdminGuard>;
}
