'use client';

import { useState, useEffect } from 'react';
import { useSkills, useCreateSkill, useUpdateSkill, useDeleteSkill, Skill } from '@/features/admin/hooks/useSkills';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Plus, Trash2, Database, Loader2, Search, Pencil } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

export default function AdminSkillsPage() {
  const { data: skills, isLoading } = useSkills();
  const { mutate: deleteSkill } = useDeleteSkill();
  const [searchTerm, setSearchTerm] = useState('');
  
  // حالة لتخزين المهارة المراد تعديلها حالياً
  const [editingSkill, setEditingSkill] = useState<Skill | null>(null);

  const filteredSkills = skills?.filter(skill => 
    skill.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between gap-4 items-start sm:items-center">
        <div>
           <h1 className="text-3xl font-bold tracking-tight">إدارة المهارات</h1>
           <p className="text-muted-foreground mt-1">قائمة بجميع المهارات التقنية المتوفرة في النظام.</p>
        </div>
        <CreateSkillDialog />
      </div>

      <Card>
        <CardHeader className="pb-3">
            <div className="flex justify-between items-center">
                <CardTitle className="text-lg font-medium">المهارات ({skills?.length || 0})</CardTitle>
                <div className="relative w-64">
                    <Search className="absolute right-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input 
                        placeholder="بحث عن مهارة..." 
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
                 {[1,2,3,4].map(i => <Skeleton key={i} className="h-12 w-full" />)}
             </div>
          ) : (
            <div className="rounded-md border">
                <Table>
                <TableHeader>
                    <TableRow>
                    <TableHead className="w-[100px]">ID</TableHead>
                    <TableHead>اسم المهارة</TableHead>
                    <TableHead className="text-left">الإجراءات</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {filteredSkills && filteredSkills.length > 0 ? (
                    filteredSkills.map((skill) => (
                        <TableRow key={skill.id}>
                        <TableCell className="font-medium">{skill.id}</TableCell>
                        <TableCell>
                            <div className="flex items-center gap-2">
                                <Database className="h-4 w-4 text-muted-foreground" />
                                <span className="font-semibold text-primary">{skill.name}</span>
                            </div>
                        </TableCell>
                        <TableCell className="text-left">
                            <div className="flex items-center gap-2">
                                {/* زر التعديل */}
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    onClick={() => setEditingSkill(skill)}
                                >
                                    <Pencil className="h-4 w-4 text-blue-500" />
                                </Button>
                                {/* زر الحذف */}
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                                    onClick={() => {
                                        if(confirm('هل أنت متأكد من حذف هذه المهارة؟')) {
                                            deleteSkill(skill.id);
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
                        لا توجد مهارات مطابقة.
                        </TableCell>
                    </TableRow>
                    )}
                </TableBody>
                </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* نافذة التعديل (تظهر فقط عند اختيار مهارة) */}
      {editingSkill && (
        <EditSkillDialog 
            skill={editingSkill} 
            open={!!editingSkill} 
            onOpenChange={(open) => !open && setEditingSkill(null)} 
        />
      )}
    </div>
  );
}

// مكون إضافة مهارة
function CreateSkillDialog() {
    const [name, setName] = useState('');
    const [open, setOpen] = useState(false);
    const { mutate: createSkill, isPending } = useCreateSkill();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;
        createSkill(name, {
            onSuccess: () => {
                setOpen(false);
                setName('');
            }
        });
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>
                    <Plus className="ml-2 h-4 w-4" />
                    إضافة مهارة جديدة
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>إضافة مهارة جديدة</DialogTitle>
                    <DialogDescription>أدخل اسم المهارة لإضافتها للنظام.</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">اسم المهارة</label>
                        <Input 
                            placeholder="مثال: Python" 
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={isPending || !name}>
                            {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
                            حفظ
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}

// مكون تعديل مهارة (الجديد)
function EditSkillDialog({ skill, open, onOpenChange }: { skill: Skill, open: boolean, onOpenChange: (open: boolean) => void }) {
    const [name, setName] = useState(skill.name);
    const { mutate: updateSkill, isPending } = useUpdateSkill();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;
        updateSkill({ id: skill.id, name }, {
            onSuccess: () => {
                onOpenChange(false);
            }
        });
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>تعديل المهارة</DialogTitle>
                    <DialogDescription>تغيير اسم المهارة: {skill.name}</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">الاسم الجديد</label>
                        <Input 
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={isPending || !name}>
                            {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
                            تحديث
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}