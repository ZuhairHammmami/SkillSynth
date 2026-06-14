// المسار: src/app/admin/users/page.tsx
import { UsersTable } from "@/features/admin/components/UsersTable";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";

export default function AdminUsersPage() {
    return (
        <Card>
            <CardHeader>
                <CardTitle>إدارة المستخدمين</CardTitle>
                <CardDescription>عرض وتحكم في جميع المستخدمين المسجلين في النظام.</CardDescription>
            </CardHeader>
            <CardContent>
                <UsersTable />
            </CardContent>
        </Card>
    );
}