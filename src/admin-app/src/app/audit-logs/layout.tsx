import { AdminLayout } from '@/app/admin-layout';
import { AdminGuard } from '@/components/AdminGuard';

export default function AuditLogsLayout({ children }: { children: React.ReactNode }) {
  return <AdminGuard><AdminLayout>{children}</AdminLayout></AdminGuard>;
}
