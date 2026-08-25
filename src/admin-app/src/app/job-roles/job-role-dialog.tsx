'use client';

import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { JobRole, Skill } from '@/types/api';

const textareaClass =
  'flex min-h-[72px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

interface JobRolePayload {
  title?: string;
  description?: string;
  career_field?: string;
  skill_ids?: number[];
}

/** Create-or-edit dialog for the job-roles table; POSTs when no role is
 *  given, PUTs /admin/job-roles/{id} otherwise. skill_ids is a multi-select
 *  of catalog skills (the role's required-skill map). */
export function JobRoleDialog({ role, open, onOpenChange }: {
  role?: JobRole;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [careerField, setCareerField] = useState('');
  const [skillIds, setSkillIds] = useState<number[]>([]);

  const { data: skills } = useQuery<Skill[]>({
    queryKey: ['skills'],
    queryFn: async () => { const res = await apiClient.get<Skill[]>('/admin/skills'); return res.data; },
    enabled: open,
  });

  useEffect(() => {
    if (open) {
      setTitle(role?.title || '');
      setDescription(role?.description || '');
      setCareerField(role?.career_field || '');
      setSkillIds(role?.skill_ids || []);
    }
  }, [open, role]);

  const saveMutation = useMutation({
    mutationFn: async (payload: JobRolePayload) => {
      if (role) await apiClient.put(`/admin/job-roles/${role.id}`, payload);
      else await apiClient.post('/admin/job-roles', payload);
    },
    onSuccess: () => {
      toast.success(role ? 'Job role updated' : 'Job role created');
      queryClient.invalidateQueries({ queryKey: ['jobRoles'] });
      onOpenChange(false);
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const toggleSkill = (id: number) => {
    setSkillIds((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
  };

  const handleSubmit = () => {
    if (!title.trim()) {
      toast.error('Job role title is required');
      return;
    }
    void saveMutation.mutateAsync({
      title: title.trim(),
      description: description.trim() || undefined,
      career_field: careerField.trim() || undefined,
      skill_ids: skillIds,
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{role ? 'Edit Job Role' : 'New Job Role'}</DialogTitle>
          <DialogDescription>Path generation targets and required skills per role</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label htmlFor="jr-title" className="text-sm font-medium">Title</label>
            <Input id="jr-title" placeholder="e.g. Frontend Developer" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="jr-desc" className="text-sm font-medium">Description</label>
            <textarea id="jr-desc" className={textareaClass} value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="jr-field" className="text-sm font-medium">Career field</label>
            <Input id="jr-field" placeholder="e.g. Engineering" value={careerField} onChange={(e) => setCareerField(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <span className="text-sm font-medium">Required skills</span>
            <div className="max-h-36 space-y-1 overflow-y-auto rounded-md border p-2">
              {(skills || []).length === 0 ? (
                <p className="py-2 text-center text-sm text-muted-foreground">No skills available</p>
              ) : (
                (skills || []).map((skill) => (
                  <label key={skill.id} className="flex cursor-pointer items-center gap-2 rounded px-1 py-0.5 text-sm hover:bg-accent">
                    <input
                      type="checkbox"
                      checked={skillIds.includes(skill.id)}
                      onChange={() => toggleSkill(skill.id)}
                      className="h-4 w-4 accent-primary"
                    />
                    {skill.name}
                  </label>
                ))
              )}
            </div>
          </div>
          <Button className="w-full" onClick={handleSubmit} disabled={!title.trim() || saveMutation.isPending}>
            {saveMutation.isPending ? 'Saving...' : role ? 'Save Changes' : 'Create Job Role'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}