'use client';

import { useState } from 'react';
import { 
  useCategories, 
  useCreateCategory, 
  useUpdateCategory, 
  useDeleteCategory, 
  Category 
} from '@/features/admin/hooks/useCategories';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, 
  DialogDescription, DialogTrigger, DialogFooter 
} from '@/components/ui/dialog';
import { Plus, Trash2, Layers, Loader2, Search, Pencil } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

export default function AdminCategoriesPage() {
  const { data: categories, isLoading } = useCategories();
  const { mutate: deleteCategory } = useDeleteCategory();
  const [searchTerm, setSearchTerm] = useState('');
  
  // حالة للتصنيف المراد تعديله
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);

  const filteredCategories = categories?.filter(cat => 
    cat.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between gap-4 items-start sm:items-center">
        <div>
           <h1 className="text-3xl font-bold tracking-tight">إدارة التصنيفات</h1>
           <p className="text-muted-foreground mt-1">تصنيف المجالات (مثل: برمجة، تصميم، تسويق).</p>
        </div>
        <CreateCategoryDialog />
      </div>

      <Card>
        <CardHeader className="pb-3">
            <div className="flex justify-between items-center">
                <CardTitle className="text-lg font-medium">التصنيفات ({categories?.length || 0})</CardTitle>
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
                    <TableHead>اسم التصنيف</TableHead>
                    <TableHead className="text-left">الإجراءات</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {filteredCategories && filteredCategories.length > 0 ? (
                    filteredCategories.map((cat) => (
                        <TableRow key={cat.id}>
                        <TableCell className="font-medium">{cat.id}</TableCell>
                        <TableCell>
                            <div className="flex items-center gap-2">
                                <Layers className="h-4 w-4 text-muted-foreground" />
                                <span className="font-semibold text-primary">{cat.name}</span>
                            </div>
                        </TableCell>
                        <TableCell className="text-left">
                            <div className="flex items-center gap-2">
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    onClick={() => setEditingCategory(cat)}
                                >
                                    <Pencil className="h-4 w-4 text-blue-500" />
                                </Button>
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                                    onClick={() => {
                                        if(confirm('هل أنت متأكد من الحذف؟')) {
                                            deleteCategory(cat.id);
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
                        لا توجد تصنيفات.
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
      {editingCategory && (
        <EditCategoryDialog 
            category={editingCategory} 
            open={!!editingCategory} 
            onOpenChange={(open) => !open && setEditingCategory(null)} 
        />
      )}
    </div>
  );
}

function CreateCategoryDialog() {
    const [name, setName] = useState('');
    const [open, setOpen] = useState(false);
    const { mutate: createCategory, isPending } = useCreateCategory();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;
        createCategory(name, {
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
                    إضافة تصنيف
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>إضافة تصنيف جديد</DialogTitle>
                    <DialogDescription>أدخل اسم التصنيف الجديد.</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">الاسم</label>
                        <Input 
                            placeholder="مثال: Development" 
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

function EditCategoryDialog({ category, open, onOpenChange }: { category: Category, open: boolean, onOpenChange: (open: boolean) => void }) {
    const [name, setName] = useState(category.name);
    const { mutate: updateCategory, isPending } = useUpdateCategory();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;
        updateCategory({ id: category.id, name }, {
            onSuccess: () => {
                onOpenChange(false);
            }
        });
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>تعديل التصنيف</DialogTitle>
                    <DialogDescription>تغيير اسم التصنيف: {category.name}</DialogDescription>
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