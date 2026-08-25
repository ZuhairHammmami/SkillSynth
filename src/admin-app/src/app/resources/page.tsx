'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { getApiErrorMessage } from '@/lib/api-error';
import { toast } from 'sonner';
import { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Trash2, ExternalLink } from 'lucide-react';
import { CreateResourceDialog } from './create-resource-dialog';
import type { Resource } from '@/types/api';

export default function ResourcesPage() {
  const { data: resources, isLoading } = useQuery<Resource[]>({
    queryKey: ['resources'],
    queryFn: async () => { const res = await apiClient.get<Resource[]>('/admin/resources'); return res.data; },
  });
  const queryClient = useQueryClient();
  const deleteResource = useMutation({
    mutationFn: async (id: number) => { await apiClient.delete(`/admin/resources/${id}`); },
    onSuccess: () => {
      toast.success('Resource deleted');
      queryClient.invalidateQueries({ queryKey: ['resources'] });
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
  const [search, setSearch] = useState('');

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const filtered = (resources || []).filter((r) => r.title.toLowerCase().includes(search.toLowerCase()));

  const handleDelete = async (id: number) => {
    if (confirm('Delete this resource?')) await deleteResource.mutateAsync(id).catch(() => undefined);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Resources</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage learning resources</p>
        </div>
        <CreateResourceDialog />
      </div>

      <Card>
        <CardHeader>
          <Input placeholder="Search resources..." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-sm" />
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Author</TableHead>
                <TableHead>Language</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground py-8">No resources found</TableCell></TableRow>
              ) : (
                filtered.map((res) => (
                  <TableRow key={res.id}>
                    <TableCell className="font-medium">
                      <a href={res.url} target="_blank" rel="noopener noreferrer" className="hover:text-primary flex items-center gap-1">
                        {res.title} <ExternalLink className="h-3 w-3" />
                      </a>
                    </TableCell>
                    <TableCell><Badge variant="secondary">{res.type}</Badge></TableCell>
                    <TableCell className="text-muted-foreground text-sm">{res.author_or_platform || '—'}</TableCell>
                    <TableCell>{res.language?.toUpperCase() || 'EN'}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(res.id)} className="text-destructive">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
