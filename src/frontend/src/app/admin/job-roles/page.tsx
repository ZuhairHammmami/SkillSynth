'use client';

import { useState } from 'react';
import { 
  useJobRoles, 
  useCreateJobRole, 
  useUpdateJobRole, 
  useDeleteJobRole, 
  JobRole 
} from '@/features/admin/hooks/useJobRoles';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table';
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, 
  DialogDescription, DialogTrigger, DialogFooter 
} from '@/shared/ui/dialog';
import { Plus, Trash2, Briefcase, Loader2, Search, Pencil } from 'lucide-react';
import { Skeleton } from '@/shared/ui/skeleton';

export default function AdminJobRolesPage() {
  const { data: jobRoles, isLoading } = useJobRoles();
  const { mutate: deleteJobRole } = useDeleteJobRole();
  const [searchTerm, setSearchTerm] = useState('');
  
  // حالة للدور المراد تعديله
  const [editingRole, setEditingRole] = useState<JobRole | null>(null);

  const filteredRoles = jobRoles?.filter(role => 
    role.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between gap-4 items-start sm:items-center">
        <div>
           <h1 className="text-3xl font-bold tracking-tight">إدارة الأدوار الوظيفية</h1>
           <p className="text-muted-foreground mt-1">المسميات الوظيفية المستهدفة (مثل: Full Stack Developer).</p>
        </div>
        <CreateJobRoleDialog />
      </div>

      <Card>
        <CardHeader className="pb-3">
            <div className="flex justify-between items-center">
                <CardTitle className="text-lg font-medium">الأدوار الوظيفية ({jobRoles?.length || 0})</CardTitle>
                <div className="relative w-64">
                    <Search className="absolute right-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input 
                        placeholder="بحث..." 
                        className="pr-8" 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
             <div className="space-y-2">
                 {[1,2,3].map(i => <Skeleton key={i} className="h-12 w-full" />)}
             </div>
          ) : (
            <div className="rounded-md border">
                <Table>
                <TableHeader>
                    <TableRow>
                    <TableHead className="w-[100px]">ID</TableHead>
                    <TableHead>المسمى الوظيفي</TableHead>
                    <TableHead className="text-left">الإجراءات</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {filteredRoles && filteredRoles.length > 0 ? (
                    filteredRoles.map((role) => (
                        <TableRow key={role.id}>
                        <TableCell className="font-medium">{role.id}</TableCell>
                        <TableCell>
                            <div className="flex items-center gap-2">
                                <Briefcase className="h-4 w-4 text-muted-foreground" />
                                <span className="font-semibold text-primary">{role.title}</span>
                            </div>
                        </TableCell>
                        <TableCell className="text-left">
                            <div className="flex items-center gap-2">
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    onClick={() => setEditingRole(role)}
                                >
                                    <Pencil className="h-4 w-4 text-blue-500" />
                                </Button>
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                                    onClick={() => {
                                        if(confirm('هل أنت متأكد من الحذف؟')) {
                                            deleteJobRole(role.id);
                                        }
                                    }}
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        </TableCell>
                        </TableRow>
                    ))
                    ) : (
                    <TableRow>
                        <TableCell colSpan={3} className="h-24 text-center text-muted-foreground">
                        لا توجد أدوار وظيفية.
                        </TableCell>
                    </TableRow>
                    )}
                </TableBody>
                </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* نافذة التعديل */}
      {editingRole && (
        <EditJobRoleDialog 
            jobRole={editingRole} 
            open={!!editingRole} 
            onOpenChange={(open) => !open && setEditingRole(null)} 
        />
      )}
    </div>
  );
}

function CreateJobRoleDialog() {
    const [title, setTitle] = useState('');
    const [open, setOpen] = useState(false);
    const { mutate: createJobRole, isPending } = useCreateJobRole();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim()) return;
        createJobRole(title, {
            onSuccess: () => {
                setOpen(false);
                setTitle('');
            }
        });
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>
                    <Plus className="ml-2 h-4 w-4" />
                    إضافة دور وظيفي
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>إضافة دور وظيفي جديد</DialogTitle>
                    <DialogDescription>أدخل عنوان الدور الوظيفي (مثل: Data Scientist).</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">العنوان</label>
                        <Input 
                            placeholder="مثال: DevOps Engineer" 
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        />
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={isPending || !title}>
                            {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
                            حفظ
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}

function EditJobRoleDialog({ jobRole, open, onOpenChange }: { jobRole: JobRole, open: boolean, onOpenChange: (open: boolean) => void }) {
    const [title, setTitle] = useState(jobRole.title);
    const { mutate: updateJobRole, isPending } = useUpdateJobRole();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim()) return;
        updateJobRole({ id: jobRole.id, title }, {
            onSuccess: () => {
                onOpenChange(false);
            }
        });
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>تعديل الدور الوظيفي</DialogTitle>
                    <DialogDescription>تغيير المسمى الوظيفي: {jobRole.title}</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">العنوان الجديد</label>
                        <Input 
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        />
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={isPending || !title}>
                            {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
                            تحديث
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}