import { AdminLayout } from '@/app/admin-layout';
import { AdminGuard } from '@/components/AdminGuard';

export default function UsersLayout({ children }: { children: React.ReactNode }) {
  return <AdminGuard><AdminLayout>{children}</AdminLayout></AdminGuard>;
}
