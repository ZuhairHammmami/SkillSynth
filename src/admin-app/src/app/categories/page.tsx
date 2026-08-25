'use client';

import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Pencil, Plus } from 'lucide-react';
import { DeleteButton } from '@/components/delete-button';
import { CategoryDialog } from './category-dialog';
import type { Category } from '@/types/api';

/** Admin Categories page: table of category rows with create/edit/delete
 *  (delete upgrades 409 dependent conflicts into a force-delete dialog). */
export default function CategoriesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Category | undefined>();

  const { data: categories, isLoading } = useQuery<Category[]>({
    queryKey: ['adminCategories'],
    queryFn: async () => { const res = await apiClient.get<Category[]>('/admin/categories'); return res.data; },
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const nameById = new Map((categories || []).map((c) => [c.id, c.name]));
  const filtered = (categories || []).filter((c) => c.name.toLowerCase().includes(search.toLowerCase()));

  const openCreate = () => {
    setEditing(undefined);
    setDialogOpen(true);
  };
  const openEdit = (category: Category) => {
    setEditing(category);
    setDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Categories</h1>
          <p className="text-sm text-muted-foreground mt-1">Organize skills into a category tree</p>
        </div>
        <Button onClick={openCreate}><Plus className="ms-2 h-4 w-4" />Add Category</Button>
      </div>

      <Card>
        <CardHeader>
          <Input placeholder="Search categories..." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-sm" />
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Parent</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground py-8">No categories found</TableCell></TableRow>
              ) : (
                filtered.map((category) => (
                  <TableRow key={category.id}>
                    <TableCell className="font-medium">{category.name}</TableCell>
                    <TableCell className="text-muted-foreground text-sm max-w-xs truncate">{category.description || '—'}</TableCell>
                    <TableCell>
                      {category.parent_id != null ? (
                        <Badge variant="secondary">{nameById.get(category.parent_id) || `#${category.parent_id}`}</Badge>
                      ) : (
                        <span className="text-muted-foreground text-sm">Top level</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => openEdit(category)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <DeleteButton
                        endpoint={`/admin/categories/${category.id}`}
                        label="category"
                        queryKeys={['adminCategories', 'skills']}
                      />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <CategoryDialog category={editing} open={dialogOpen} onOpenChange={(open) => {
        setDialogOpen(open);
        if (!open) queryClient.invalidateQueries({ queryKey: ['adminCategories'] });
      }} />
    </div>
  );
}