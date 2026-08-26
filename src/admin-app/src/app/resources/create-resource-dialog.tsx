'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plus } from 'lucide-react';

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50';

const RESOURCE_TYPES = ['course', 'video', 'book', 'article', 'practice', 'documentation', 'interactive'] as const;
const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'ar', label: 'Arabic' },
] as const;

interface CreateResourcePayload {
  title: string;
  url: string;
  type: string;
  is_free: boolean;
  is_official: boolean;
  author_or_platform?: string;
  language: string;
}

export function CreateResourceDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const [type, setType] = useState('course');
  const [language, setLanguage] = useState('en');
  const [isFree, setIsFree] = useState(true);
  const [isOfficial, setIsOfficial] = useState(false);
  const [author, setAuthor] = useState('');

  const createResource = useMutation({
    mutationFn: async (payload: CreateResourcePayload) => {
      const res = await apiClient.post('/admin/resources', payload);
      return res.data;
    },
    onSuccess: (_data, payload) => {
      toast.success(`Resource "${payload.title}" created`);
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      setOpen(false);
      setTitle('');
      setUrl('');
      setType('course');
      setLanguage('en');
      setIsFree(true);
      setIsOfficial(false);
      setAuthor('');
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });

  const urlValid = /^https?:\/\/\S+/.test(url.trim());
  const canSubmit = title.trim().length > 0 && urlValid && !createResource.isPending;

  const handleSubmit = () => {
    if (!canSubmit) {
      toast.error('Title is required and URL must start with http:// or https://');
      return;
    }
    void createResource.mutateAsync({
      title: title.trim(),
      url: url.trim(),
      type,
      is_free: isFree,
      is_official: isOfficial,
      author_or_platform: author.trim() || undefined,
      language,
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button><Plus className="ms-2 h-4 w-4" />Add Resource</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Resource</DialogTitle>
          <DialogDescription>Add a new learning resource to the catalog</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label htmlFor="cr-title" className="text-sm font-medium">Title</label>
            <Input id="cr-title" placeholder="e.g. React Documentation" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cr-url" className="text-sm font-medium">URL</label>
            <Input id="cr-url" type="url" placeholder="https://example.com/learn" value={url} onChange={(e) => setUrl(e.target.value)} />
            {url.length > 0 && !urlValid && (
              <p className="text-xs text-destructive">URL must start with http:// or https://</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label htmlFor="cr-type" className="text-sm font-medium">Type</label>
              <select id="cr-type" className={selectClass} value={type} onChange={(e) => setType(e.target.value)}>
                {RESOURCE_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label htmlFor="cr-lang" className="text-sm font-medium">Language</label>
              <select id="cr-lang" className={selectClass} value={language} onChange={(e) => setLanguage(e.target.value)}>
                {LANGUAGES.map((l) => (
                  <option key={l.value} value={l.value}>{l.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="space-y-1.5">
            <label htmlFor="cr-author" className="text-sm font-medium">Author / platform (optional)</label>
            <Input id="cr-author" placeholder="e.g. Microsoft" value={author} onChange={(e) => setAuthor(e.target.value)} />
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
            {createResource.isPending ? 'Creating...' : 'Create Resource'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
