'use client';

import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Pencil } from 'lucide-react';
import type { Category, Skill } from '@/types/api';

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';
const textareaClass =
  'flex min-h-[72px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

interface EditSkillPayload {
  name?: string;
  description?: string;
  difficulty_level?: number;
  estimated_hours?: number;
  icon?: string;
  color?: string;
  category_id?: number | null;
  prerequisite_ids?: number[];
}

/** Edit dialog for one skills-table row; PUTs /admin/skills/{id}. Category
 *  is a single select and prerequisites a multi-select of other skills.
 *  Rendered by skills/page.tsx. */
export function EditSkillDialog({ skill }: { skill: Skill }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState(skill.name);
  const [description, setDescription] = useState(skill.description || '');
  const [difficulty, setDifficulty] = useState(skill.difficulty_level ? String(skill.difficulty_level) : '');
  const [hours, setHours] = useState(skill.estimated_hours != null ? String(skill.estimated_hours) : '');
  const [categoryId, setCategoryId] = useState(skill.category_id != null ? String(skill.category_id) : '');
  const [prereqIds, setPrereqIds] = useState<number[]>(skill.prerequisite_ids || []);

  const { data: categories } = useQuery<Category[]>({
    queryKey: ['adminCategories'],
    queryFn: async () => { const res = await apiClient.get<Category[]>('/admin/categories'); return res.data; },
    enabled: open,
  });
  const { data: allSkills } = useQuery<Skill[]>({
    queryKey: ['skills'],
    queryFn: async () => { const res = await apiClient.get<Skill[]>('/admin/skills'); return res.data; },
    enabled: open,
  });

  useEffect(() => {
    if (open) {
      setName(skill.name);
      setDescription(skill.description || '');
      setDifficulty(skill.difficulty_level ? String(skill.difficulty_level) : '');
      setHours(skill.estimated_hours != null ? String(skill.estimated_hours) : '');
      setCategoryId(skill.category_id != null ? String(skill.category_id) : '');
      setPrereqIds(skill.prerequisite_ids || []);
    }
  }, [open, skill]);

  const updateSkill = useMutation({
    mutationFn: async (payload: EditSkillPayload) => {
      await apiClient.put(`/admin/skills/${skill.id}`, payload);
    },
    onSuccess: () => {
      toast.success('Skill updated');
      queryClient.invalidateQueries({ queryKey: ['skills'] });
      setOpen(false);
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const otherSkills = (allSkills || []).filter((s) => s.id !== skill.id);
  const togglePrereq = (id: number) => {
    setPrereqIds((prev) => (prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]));
  };

  const handleSubmit = () => {
    if (!name.trim()) {
      toast.error('Skill name is required');
      return;
    }
    void updateSkill.mutateAsync({
      name: name.trim(),
      description: description.trim() || undefined,
      difficulty_level: difficulty ? Number(difficulty) : undefined,
      estimated_hours: hours !== '' ? Number(hours) : undefined,
      category_id: categoryId === '' ? null : Number(categoryId),
      prerequisite_ids: prereqIds,
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button variant="ghost" size="icon" onClick={() => setOpen(true)}>
        <Pencil className="h-4 w-4" />
      </Button>
      <DialogContent className="max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Skill</DialogTitle>
          <DialogDescription>Update catalog details for this skill</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label htmlFor={`es-name-${skill.id}`} className="text-sm font-medium">Name</label>
            <Input id={`es-name-${skill.id}`} value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor={`es-desc-${skill.id}`} className="text-sm font-medium">Description</label>
            <textarea id={`es-desc-${skill.id}`} className={textareaClass} value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label htmlFor={`es-diff-${skill.id}`} className="text-sm font-medium">Difficulty (1-10)</label>
              <select id={`es-diff-${skill.id}`} className={selectClass} value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                <option value="">Not set</option>
                {Array.from({ length: 10 }, (_, i) => i + 1).map((n) => (<option key={n} value={n}>{n}</option>))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label htmlFor={`es-hours-${skill.id}`} className="text-sm font-medium">Estimated hours</label>
              <Input id={`es-hours-${skill.id}`} type="number" min={0} value={hours} onChange={(e) => setHours(e.target.value)} />
            </div>
          </div>
          <div className="space-y-1.5">
            <label htmlFor={`es-cat-${skill.id}`} className="text-sm font-medium">Category</label>
            <select id={`es-cat-${skill.id}`} className={selectClass} value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              <option value="">Uncategorized</option>
              {(categories || []).map((cat) => (<option key={cat.id} value={cat.id}>{cat.name}</option>))}
            </select>
          </div>
          <div className="space-y-1.5">
            <span className="text-sm font-medium">Prerequisites</span>
            <div className="max-h-36 space-y-1 overflow-y-auto rounded-md border p-2">
              {otherSkills.length === 0 ? (
                <p className="py-2 text-center text-sm text-muted-foreground">No other skills available</p>
              ) : (
                otherSkills.map((s) => (
                  <label key={s.id} className="flex cursor-pointer items-center gap-2 rounded px-1 py-0.5 text-sm hover:bg-accent">
                    <input
                      type="checkbox"
                      checked={prereqIds.includes(s.id)}
                      onChange={() => togglePrereq(s.id)}
                      className="h-4 w-4 accent-primary"
                    />
                    {s.name}
                  </label>
                ))
              )}
            </div>
          </div>
          <Button className="w-full" onClick={handleSubmit} disabled={!name.trim() || updateSkill.isPending}>
            {updateSkill.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}