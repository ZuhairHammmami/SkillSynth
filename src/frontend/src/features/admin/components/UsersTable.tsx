'use client';

import { useState } from "react";
import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    useReactTable,
    getPaginationRowModel,
    getFilteredRowModel,
} from "@tanstack/react-table";
import { useAdminUsers, useUpdateAdminUser } from "../hooks/useAdminUsers";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table';
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Skeleton } from "@/shared/ui/skeleton";
import { Badge } from "@/shared/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/shared/ui/dialog';
import { Pencil, Search, Shield, ShieldAlert, User as UserIcon, Loader2 } from "lucide-react";
import type { User } from '@/shared/store/authStore';

export function UsersTable() {
    const { data: users, isLoading } = useAdminUsers();
    const [globalFilter, setGlobalFilter] = useState("");
    const [editingUser, setEditingUser] = useState<User | null>(null);

    const columns: ColumnDef<User>[] = [
        { accessorKey: "id", header: "ID" },
        { 
            accessorKey: "full_name", 
            header: "الاسم الكامل",
            cell: ({ row }) => <span className="font-medium">{row.original.full_name}</span>
        },
        { accessorKey: "email", header: "البريد الإلكتروني" },
        { 
            accessorKey: "is_admin", 
            header: "الدور",
            cell: ({ row }) => (
                <Badge variant={row.original.is_admin ? "default" : "secondary"} className="gap-1">
                    {row.original.is_admin ? <ShieldAlert className="h-3 w-3" /> : <UserIcon className="h-3 w-3" />}
                    {row.original.is_admin ? "مسؤول (Admin)" : "مستخدم"}
                </Badge>
            ),
        },
        {
            id: "actions",
            header: "الإجراءات",
            cell: ({ row }) => {
                return (
                    <Button variant="ghost" size="sm" onClick={() => setEditingUser(row.original)}>
                        <Pencil className="h-4 w-4 text-blue-600" />
                        <span className="sr-only">تعديل</span>
                    </Button>
                );
            },
        },
    ];

    const table = useReactTable({
        data: users || [],
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        state: { globalFilter },
        onGlobalFilterChange: setGlobalFilter,
    });

    if (isLoading) {
        return <div className="space-y-2">{[1, 2, 3].map(i => <Skeleton key={i} className="h-12 w-full" />)}</div>;
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2">
                <Search className="h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="بحث عن مستخدم..."
                    value={globalFilter ?? ""}
                    onChange={(event) => setGlobalFilter(event.target.value)}
                    className="max-w-sm"
                />
            </div>
            
            <div className="rounded-md border bg-card">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => (
                                    <TableHead key={header.id}>
                                        {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                                    </TableHead>
                                ))}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <TableRow key={row.id}>
                                    {row.getVisibleCells().map((cell) => (
                                        <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="h-24 text-center">لا توجد نتائج.</TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* نافذة تعديل المستخدم */}
            {editingUser && (
                <EditUserDialog 
                    user={editingUser} 
                    open={!!editingUser} 
                    onOpenChange={(open) => !open && setEditingUser(null)} 
                />
            )}
        </div>
    );
}

function EditUserDialog({ user, open, onOpenChange }: { user: User, open: boolean, onOpenChange: (open: boolean) => void }) {
    const { mutate: updateUser, isPending } = useUpdateAdminUser();
    
    // Form State
    const [fullName, setFullName] = useState(user.full_name || "");
    const [email, setEmail] = useState(user.email);
    const [isAdmin, setIsAdmin] = useState(user.is_admin);
    const [newPassword, setNewPassword] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        
        // تجهيز البيانات للإرسال
        const payload: any = {
            full_name: fullName,
            email: email,
            is_admin: isAdmin,
        };

        // إضافة كلمة المرور فقط إذا تم إدخالها
        if (newPassword.trim()) {
            payload.password = newPassword;
        }

        updateUser({ id: String(user.id), data: payload }, {
            onSuccess: () => onOpenChange(false)
        });
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>تعديل بيانات المستخدم</DialogTitle>
                    <DialogDescription>
                        قم بتعديل بيانات {user.full_name}. اترك حقل كلمة المرور فارغاً إذا لم ترد تغييرها.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-2">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">الاسم الكامل</label>
                        <Input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium">البريد الإلكتروني</label>
                        <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                    </div>
                    
                    <div className="space-y-2 p-3 bg-muted/30 rounded-md border">
                        <div className="flex items-center gap-2">
                            <input 
                                type="checkbox" 
                                id="isAdmin" 
                                checked={isAdmin} 
                                onChange={(e) => setIsAdmin(e.target.checked)}
                                className="h-4 w-4 text-primary rounded"
                            />
                            <label htmlFor="isAdmin" className="text-sm font-medium cursor-pointer flex items-center gap-1">
                                <Shield className="h-3 w-3" />
                                منح صلاحيات مسؤول (Admin)
                            </label>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1 mr-6">
                            تنبيه: المسؤول لديه حق الوصول الكامل للوحة التحكم.
                        </p>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-blue-600">تعيين كلمة مرور جديدة (اختياري)</label>
                        <Input 
                            type="password" 
                            placeholder="أدخل كلمة مرور جديدة فقط للتغيير" 
                            value={newPassword} 
                            onChange={(e) => setNewPassword(e.target.value)} 
                        />
                    </div>

                    <DialogFooter>
                        <Button type="submit" disabled={isPending}>
                            {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
                            حفظ التغييرات
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}