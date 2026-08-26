import { AdminLayout } from '@/app/admin-layout';
import { AdminGuard } from '@/components/AdminGuard';

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  return <AdminGuard><AdminLayout>{children}</AdminLayout></AdminGuard>;
}
