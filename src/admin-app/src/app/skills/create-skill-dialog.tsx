'use client';

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus } from 'lucide-react';
import type { Category } from '@/types/api';

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';
const textareaClass =
  'flex min-h-[72px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

interface CreateSkillPayload {
  name: string;
  description?: string;
  difficulty_level?: number;
  category_ids: number[];
}

export function CreateSkillDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [categoryIds, setCategoryIds] = useState<number[]>([]);

  const { data: categories } = useQuery<Category[]>({
    queryKey: ['adminCategories'],
    queryFn: async () => { const res = await apiClient.get<Category[]>('/admin/categories'); return res.data; },
    enabled: open,
  });

  const createSkill = useMutation({
    mutationFn: async (payload: CreateSkillPayload) => {
      const res = await apiClient.post('/admin/skills', payload);
      return res.data;
    },
    onSuccess: (_data, payload) => {
      toast.success(`Skill "${payload.name}" created`);
      queryClient.invalidateQueries({ queryKey: ['skills'] });
      setOpen(false);
      setName('');
      setDescription('');
      setDifficulty('');
      setCategoryIds([]);
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const toggleCategory = (id: number) => {
    setCategoryIds((prev) => (prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]));
  };

  const handleSubmit = () => {
    if (!name.trim()) {
      toast.error('Skill name is required');
      return;
    }
    void createSkill.mutateAsync({
      name: name.trim(),
      description: description.trim() || undefined,
      difficulty_level: difficulty ? Number(difficulty) : undefined,
      category_ids: categoryIds,
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button><Plus className="ms-2 h-4 w-4" />Add Skill</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Skill</DialogTitle>
          <DialogDescription>Create a new skill in the catalog</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label htmlFor="cs-name" className="text-sm font-medium">Name</label>
            <Input id="cs-name" placeholder="e.g. React" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cs-desc" className="text-sm font-medium">Description</label>
            <textarea id="cs-desc" className={textareaClass} placeholder="What this skill covers" value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cs-diff" className="text-sm font-medium">Difficulty level (1-10)</label>
            <select id="cs-diff" className={selectClass} value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option value="">Not set</option>
              {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <span className="text-sm font-medium">Categories</span>
            <div className="max-h-36 space-y-1 overflow-y-auto rounded-md border p-2">
              {(categories || []).length === 0 ? (
                <p className="py-2 text-center text-sm text-muted-foreground">No categories available</p>
              ) : (
                (categories || []).map((cat) => (
                  <label key={cat.id} className="flex cursor-pointer items-center gap-2 rounded px-1 py-0.5 text-sm hover:bg-accent">
                    <input
                      type="checkbox"
                      checked={categoryIds.includes(cat.id)}
                      onChange={() => toggleCategory(cat.id)}
                      className="h-4 w-4 accent-primary"
                    />
                    {cat.name}
                  </label>
                ))
              )}
            </div>
          </div>
          <Button className="w-full" onClick={handleSubmit} disabled={!name.trim() || createSkill.isPending}>
            {createSkill.isPending ? 'Creating...' : 'Create Skill'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
