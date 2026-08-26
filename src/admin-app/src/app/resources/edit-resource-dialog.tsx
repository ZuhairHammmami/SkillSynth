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
import type { Resource, Skill } from '@/types/api';

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

const RESOURCE_TYPES = ['course', 'video', 'book', 'article', 'practice', 'documentation', 'interactive'] as const;
const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'ar', label: 'Arabic' },
] as const;

interface EditResourcePayload {
  title?: string;
  url?: string;
  type?: string;
  language?: string;
  is_free?: boolean | null;
  is_official?: boolean | null;
  author_or_platform?: string;
  skill_id?: number | null;
}

/** Edit dialog for one resources-table row; PUTs /admin/resources/{id}.
 *  Rendered by resources/page.tsx. */
export function EditResourceDialog({ resource }: { resource: Resource }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState(resource.title);
  const [url, setUrl] = useState(resource.url);
  const [type, setType] = useState(resource.type);
  const [language, setLanguage] = useState(resource.language || 'en');
  const [isFree, setIsFree] = useState(Boolean(resource.is_free));
  const [isOfficial, setIsOfficial] = useState(Boolean(resource.is_official));
  const [author, setAuthor] = useState(resource.author_or_platform || '');
  const [skillId, setSkillId] = useState(resource.skill_id != null ? String(resource.skill_id) : '');

  const { data: skills } = useQuery<Skill[]>({
    queryKey: ['skills'],
    queryFn: async () => { const res = await apiClient.get<Skill[]>('/admin/skills'); return res.data; },
    enabled: open,
  });

  useEffect(() => {
    if (open) {
      setTitle(resource.title);
      setUrl(resource.url);
      setType(resource.type);
      setLanguage(resource.language || 'en');
      setIsFree(Boolean(resource.is_free));
      setIsOfficial(Boolean(resource.is_official));
      setAuthor(resource.author_or_platform || '');
      setSkillId(resource.skill_id != null ? String(resource.skill_id) : '');
    }
  }, [open, resource]);

  const updateResource = useMutation({
    mutationFn: async (payload: EditResourcePayload) => {
      await apiClient.put(`/admin/resources/${resource.id}`, payload);
    },
    onSuccess: () => {
      toast.success('Resource updated');
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      setOpen(false);
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const urlValid = /^https?:\/\/\S+/.test(url.trim());
  const canSubmit = title.trim().length > 0 && urlValid && !updateResource.isPending;

  const handleSubmit = () => {
    if (!canSubmit) {
      toast.error('Title is required and URL must start with http:// or https://');
      return;
    }
    void updateResource.mutateAsync({
      title: title.trim(),
      url: url.trim(),
      type,
      language,
      is_free: isFree,
      is_official: isOfficial,
      author_or_platform: author.trim() || undefined,
      skill_id: skillId === '' ? null : Number(skillId),
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button variant="ghost" size="icon" onClick={() => setOpen(true)}>
        <Pencil className="h-4 w-4" />
      </Button>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Resource</DialogTitle>
          <DialogDescription>Update this catalog resource</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label htmlFor={`er-title-${resource.id}`} className="text-sm font-medium">Title</label>
            <Input id={`er-title-${resource.id}`} value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor={`er-url-${resource.id}`} className="text-sm font-medium">URL</label>
            <Input id={`er-url-${resource.id}`} type="url" value={url} onChange={(e) => setUrl(e.target.value)} />
            {url.length > 0 && !urlValid && (
              <p className="text-xs text-destructive">URL must start with http:// or https://</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label htmlFor={`er-type-${resource.id}`} className="text-sm font-medium">Type</label>
              <select id={`er-type-${resource.id}`} className={selectClass} value={type} onChange={(e) => setType(e.target.value)}>
                {RESOURCE_TYPES.map((t) => (<option key={t} value={t}>{t}</option>))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label htmlFor={`er-lang-${resource.id}`} className="text-sm font-medium">Language</label>
              <select id={`er-lang-${resource.id}`} className={selectClass} value={language} onChange={(e) => setLanguage(e.target.value)}>
                {LANGUAGES.map((l) => (<option key={l.value} value={l.value}>{l.label}</option>))}
              </select>
            </div>
          </div>
          <div className="space-y-1.5">
            <label htmlFor={`er-skill-${resource.id}`} className="text-sm font-medium">Linked skill</label>
            <select id={`er-skill-${resource.id}`} className={selectClass} value={skillId} onChange={(e) => setSkillId(e.target.value)}>
              <option value="">Unlinked</option>
              {(skills || []).map((s) => (<option key={s.id} value={s.id}>{s.name}</option>))}
            </select>
          </div>
          <div className="space-y-1.5">
            <label htmlFor={`er-author-${resource.id}`} className="text-sm font-medium">Author / platform (optional)</label>
            <Input id={`er-author-${resource.id}`} value={author} onChange={(e) => setAuthor(e.target.value)} />
          </div>
          <div className="flex gap-6">
            <label className="flex cursor-pointer items-center gap-2 text-sm font-medium">
              <input type="checkbox" checked={isFree} onChange={(e) => setIsFree(e.target.checked)} className="h-4 w-4 accent-primary" />
              Free
            </label>
            <label className="flex cursor-pointer items-center gap-2 text-sm font-medium">
              <input type="checkbox" checked={isOfficial} onChange={(e) => setIsOfficial(e.target.checked)} className="h-4 w-4 accent-primary" />
              Official
            </label>
          </div>
          <Button className="w-full" onClick={handleSubmit} disabled={!canSubmit}>
            {updateResource.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}