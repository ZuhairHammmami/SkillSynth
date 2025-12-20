// المسار: src/app/admin/dashboard/page.tsx
import { AdminGuard } from "@/features/auth/components/AdminGuard"; // سننشئه الآن

function AdminDashboardContent() {
    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold">لوحة تحكم الأدمن</h1>
            <p className="text-muted-foreground">مرحباً بك. هنا يمكنك إدارة المستخدمين والمحتوى.</p>
            {/* هنا سنضيف جداول وتقارير الأدمن لاحقًا */}
        </div>
    );
}

export default function AdminDashboardPage() {
    return (
        <AdminGuard>
            <AdminDashboardContent />
        </AdminGuard>
    )
}