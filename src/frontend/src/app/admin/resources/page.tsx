'use client';

import { useState, useEffect } from 'react';
import { useResources, useCreateResource, useUpdateResource, useDeleteResource, Resource, ResourceData } from '@/features/admin/hooks/useResources';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger, DialogFooter } from '@/shared/ui/dialog';
import { Plus, Trash2, Pencil, BookOpen, Loader2, Search, ExternalLink, Video, FileText } from 'lucide-react';
import { Skeleton } from '@/shared/ui/skeleton';
import { Badge } from '@/shared/ui/badge';

export default function AdminResourcesPage() {
  const { data: resources, isLoading } = useResources();
  const { mutate: deleteResource } = useDeleteResource();
  const [searchTerm, setSearchTerm] = useState('');
  const [editingResource, setEditingResource] = useState<Resource | null>(null);

  const filteredResources = resources?.filter(res => 
    res.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    res.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getTypeIcon = (type: string) => {
      if (type === 'Video') return <Video className="h-4 w-4 text-blue-500" />;
      if (type === 'Course') return <BookOpen className="h-4 w-4 text-green-500" />;
      return <FileText className="h-4 w-4 text-gray-500" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between gap-4 items-start sm:items-center">
        <div>
           <h1 className="text-3xl font-bold tracking-tight">إدارة المصادر</h1>
           <p className="text-muted-foreground mt-1">المحتوى التعليمي (فيديوهات، مقالات، كورسات).</p>
        </div>
        <CreateResourceDialog />
      </div>

      <Card>
        <CardHeader className="pb-3">
            <div className="flex justify-between items-center">
                <CardTitle className="text-lg font-medium">المصادر ({resources?.length || 0})</CardTitle>
                <div className="relative w-64">
                    <Search className="absolute right-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input 
                        placeholder="بحث في المصادر..." 
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
                    <TableHead className="w-[60px]">ID</TableHead>
                    <TableHead>العنوان</TableHead>
                    <TableHead>النوع</TableHead>
                    <TableHead>المنصة/المؤلف</TableHead>
                    <TableHead>التكلفة</TableHead>
                    <TableHead className="text-left">الإجراءات</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {filteredResources && filteredResources.length > 0 ? (
                    filteredResources.map((res) => (
                        <TableRow key={res.id}>
                        <TableCell className="font-medium">{res.id}</TableCell>
                        <TableCell>
                            <div className="flex items-center gap-2">
                                <a href={res.url} target="_blank" rel="noreferrer" className="hover:underline flex items-center gap-1 font-medium">
                                    {res.title}
                                    <ExternalLink className="h-3 w-3 opacity-50" />
                                </a>
                            </div>
                        </TableCell>
                        <TableCell>
                            <div className="flex items-center gap-2">
                                {getTypeIcon(res.type)}
                                <span>{res.type}</span>
                            </div>
                        </TableCell>
                        <TableCell>{res.author_or_platform || '-'}</TableCell>
                        <TableCell>
                            <Badge variant={res.is_free ? "secondary" : "default"} className={res.is_free ? "bg-green-100 text-green-800 hover:bg-green-100" : ""}>
                                {res.is_free ? "مجاني" : "مدفوع"}
                            </Badge>
                        </TableCell>
                        <TableCell className="text-left">
                            <div className="flex items-center gap-2">
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    onClick={() => setEditingResource(res)}
                                >
                                    <Pencil className="h-4 w-4 text-blue-500" />
                                </Button>
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                                    onClick={() => {
                                        if(confirm('هل أنت متأكد من حذف هذا المصدر؟')) {
                                            deleteResource(res.id);
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
                        <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                        لا توجد مصادر مطابقة.
                        </TableCell>
                    </TableRow>
                    )}
                </TableBody>
                </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      {editingResource && (
        <EditResourceDialog 
            resource={editingResource} 
            open={!!editingResource} 
            onOpenChange={(open) => !open && setEditingResource(null)} 
        />
      )}
    </div>
  );
}

// مكون فرعي: النموذج (مشترك للإضافة والتعديل لتجنب التكرار)
function ResourceForm({ 
    initialData, 
    onSubmit, 
    isPending, 
    buttonText 
}: { 
    initialData?: ResourceData, 
    onSubmit: (data: ResourceData) => void, 
    isPending: boolean, 
    buttonText: string 
}) {
    const [title, setTitle] = useState(initialData?.title || '');
    const [url, setUrl] = useState(initialData?.url || '');
    const [type, setType] = useState(initialData?.type || 'Video');
    const [author, setAuthor] = useState(initialData?.author_or_platform || '');
    const [isFree, setIsFree] = useState(initialData?.is_free ?? true);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({ title, url, type, is_free: isFree, author_or_platform: author || undefined });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4 py-2">
            <div className="space-y-2">
                <label className="text-sm font-medium">العنوان</label>
                <Input 
                    placeholder="مثال: Python for Beginners Full Course" 
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                />
            </div>
            
            <div className="space-y-2">
                <label className="text-sm font-medium">رابط المصدر (URL)</label>
                <Input 
                    placeholder="https://..." 
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    required
                />
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium">النوع</label>
                    <select 
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                        value={type}
                        onChange={(e) => setType(e.target.value)}
                    >
                        <option value="Video">Video</option>
                        <option value="Article">Article</option>
                        <option value="Course">Course</option>
                        <option value="Book">Book</option>
                        <option value="Documentation">Documentation</option>
                    </select>
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium">المنصة / المؤلف</label>
                    <Input 
                        placeholder="Udemy, Coursera..." 
                        value={author}
                        onChange={(e) => setAuthor(e.target.value)}
                    />
                </div>
            </div>

            <div className="flex items-center space-x-2 pt-2">
                <input
                    type="checkbox"
                    id="isFree"
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                    checked={isFree}
                    onChange={(e) => setIsFree(e.target.checked)}
                />
                <label htmlFor="isFree" className="text-sm font-medium leading-none">هذا المصدر مجاني</label>
            </div>

            <DialogFooter className="pt-4">
                <Button type="submit" disabled={isPending || !title || !url}>
                    {isPending && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
                    {buttonText}
                </Button>
            </DialogFooter>
        </form>
    );
}

function CreateResourceDialog() {
    const [open, setOpen] = useState(false);
    const { mutate: createResource, isPending } = useCreateResource();
    
    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button><Plus className="ml-2 h-4 w-4" /> إضافة مصدر</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>إضافة مصدر جديد</DialogTitle>
                    <DialogDescription>أدخل تفاصيل المصدر.</DialogDescription>
                </DialogHeader>
                <ResourceForm 
                    isPending={isPending} 
                    buttonText="حفظ المصدر" 
                    onSubmit={(data) => createResource(data, { onSuccess: () => setOpen(false) })} 
                />
            </DialogContent>
        </Dialog>
    );
}

function EditResourceDialog({ resource, open, onOpenChange }: { resource: Resource, open: boolean, onOpenChange: (open: boolean) => void }) {
    const { mutate: updateResource, isPending } = useUpdateResource();

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>تعديل المصدر</DialogTitle>
                    <DialogDescription>تحديث بيانات المصدر: {resource.title}</DialogDescription>
                </DialogHeader>
                <ResourceForm 
                    initialData={resource}
                    isPending={isPending} 
                    buttonText="تحديث المصدر" 
                    onSubmit={(data) => updateResource({ id: resource.id, data }, { onSuccess: () => onOpenChange(false) })} 
                />
            </DialogContent>
        </Dialog>
    );
}