'use client';

import { useAdminPaths } from '@/features/admin/hooks/useAdminPaths';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card';
import { Badge } from '@/shared/ui/badge';
import { Button } from '@/shared/ui/button';
import { Skeleton } from '@/shared/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui/table';
import { FileText, Eye, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function AdminPathsPage() {
  const { data: paths, isLoading, isError } = useAdminPaths();

  // حالة التحميل
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Card>
          <CardHeader>
             <Skeleton className="h-6 w-32 mb-2" />
             <Skeleton className="h-4 w-64" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
               <Skeleton className="h-12 w-full" />
               <Skeleton className="h-12 w-full" />
               <Skeleton className="h-12 w-full" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // حالة الخطأ (مثلاً الـ API غير موجود)
  if (isError) {
    return (
        <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
            <div className="bg-destructive/10 p-4 rounded-full">
                <AlertCircle className="h-10 w-10 text-destructive" />
            </div>
            <h2 className="text-xl font-semibold">فشل تحميل المسارات</h2>
            <p className="text-muted-foreground max-w-md">
                تعذر الاتصال بقاعدة البيانات. تأكد من أن السيرفر يعمل وأن نقطة الاتصال 
                <code className="mx-1 bg-muted px-1 py-0.5 rounded text-xs">/api/admin/paths</code>
                مفعلة.
            </p>
        </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
           <h1 className="text-3xl font-bold tracking-tight">إدارة المسارات</h1>
           <p className="text-muted-foreground mt-1">استعراض جميع المسارات التعليمية التي تم إنشاؤها.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
            <CardTitle>كل المسارات ({paths?.length || 0})</CardTitle>
            <CardDescription>قائمة بجميع المسارات المولدة من قبل المستخدمين.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>عنوان المسار</TableHead>
                  <TableHead>المستخدم</TableHead>
                  <TableHead>المدة المقدرة</TableHead>
                  <TableHead>الحالة</TableHead>
                  <TableHead className="text-left">الإجراءات</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paths && paths.length > 0 ? (
                  paths.map((path) => (
                    <TableRow key={path.id}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-muted-foreground" />
                            {path.title}
                        </div>
                      </TableCell>
                      <TableCell>{path.user_email}</TableCell>
                      <TableCell>{path.total_estimated_hours} ساعة</TableCell>
                      <TableCell>
                        <Badge variant={path.is_completed ? "default" : "outline"}>
                          {path.is_completed ? "مكتمل" : "قيد التعلم"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-left">
                        <Button variant="ghost" size="sm" asChild>
                            <Link href={`/paths/${path.id}`}>
                                <Eye className="h-4 w-4 ml-2" />
                                عرض التفاصيل
                            </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} className="h-24 text-center">
                      لا توجد مسارات حتى الآن.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}