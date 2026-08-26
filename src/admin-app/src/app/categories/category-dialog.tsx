'use client';

import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { Category } from '@/types/api';

const textareaClass =
  'flex min-h-[72px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';
const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

interface CategoryPayload {
  name?: string;
  description?: string;
  parent_id?: number | null;
}

/** Create-or-edit dialog for the categories table; POSTs when no category
 *  is given, PUTs /admin/categories/{id} otherwise. "No parent" sends an
 *  explicit null parent_id so the backend detaches the category. */
export function CategoryDialog({ category, open, onOpenChange }: {
  category?: Category;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [parentId, setParentId] = useState('');

  const { data: categories } = useQuery<Category[]>({
    queryKey: ['adminCategories'],
    queryFn: async () => { const res = await apiClient.get<Category[]>('/admin/categories'); return res.data; },
    enabled: open,
  });

  useEffect(() => {
    if (open) {
      setName(category?.name || '');
      setDescription(category?.description || '');
      setParentId(category?.parent_id != null ? String(category.parent_id) : '');
    }
  }, [open, category]);

  const saveMutation = useMutation({
    mutationFn: async (payload: CategoryPayload) => {
      if (category) await apiClient.put(`/admin/categories/${category.id}`, payload);
      else await apiClient.post('/admin/categories', payload);
    },
    onSuccess: () => {
      toast.success(category ? 'Category updated' : 'Category created');
      queryClient.invalidateQueries({ queryKey: ['adminCategories'] });
      queryClient.invalidateQueries({ queryKey: ['skills'] });
      onOpenChange(false);
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const parents = (categories || []).filter((c) => c.id !== category?.id);
  const handleSubmit = () => {
    if (!name.trim()) {
      toast.error('Category name is required');
      return;
    }
    void saveMutation.mutateAsync({
      name: name.trim(),
      description: description.trim() || undefined,
      parent_id: parentId === '' ? null : Number(parentId),
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{category ? 'Edit Category' : 'New Category'}</DialogTitle>
          <DialogDescription>Group skills under a browsable category tree</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label htmlFor="cat-name" className="text-sm font-medium">Name</label>
            <Input id="cat-name" placeholder="e.g. Frontend" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cat-desc" className="text-sm font-medium">Description</label>
            <textarea id="cat-desc" className={textareaClass} value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cat-parent" className="text-sm font-medium">Parent category</label>
            <select id="cat-parent" className={selectClass} value={parentId} onChange={(e) => setParentId(e.target.value)}>
              <option value="">None (top level)</option>
              {parents.map((c) => (<option key={c.id} value={c.id}>{c.name}</option>))}
            </select>
          </div>
          <Button className="w-full" onClick={handleSubmit} disabled={!name.trim() || saveMutation.isPending}>
            {saveMutation.isPending ? 'Saving...' : category ? 'Save Changes' : 'Create Category'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}