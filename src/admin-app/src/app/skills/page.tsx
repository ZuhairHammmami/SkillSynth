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
import { Trash2 } from 'lucide-react';
import { CreateSkillDialog } from './create-skill-dialog';
import type { Skill } from '@/types/api';

export default function SkillsPage() {
  const { data: skills, isLoading } = useQuery<Skill[]>({
    queryKey: ['skills'],
    queryFn: async () => { const res = await apiClient.get<Skill[]>('/admin/skills'); return res.data; },
  });
  const queryClient = useQueryClient();
  const deleteSkill = useMutation({
    mutationFn: async (id: number) => { await apiClient.delete(`/admin/skills/${id}`); },
    onSuccess: () => {
      toast.success('Skill deleted');
      queryClient.invalidateQueries({ queryKey: ['skills'] });
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
  const [search, setSearch] = useState('');

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const filtered = (skills || []).filter((s) => s.name.toLowerCase().includes(search.toLowerCase()));

  const handleDelete = async (id: number) => {
    if (confirm('Delete this skill?')) await deleteSkill.mutateAsync(id).catch(() => undefined);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Skills</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage the skill catalog</p>
        </div>
        <CreateSkillDialog />
      </div>

      <Card>
        <CardHeader>
          <Input placeholder="Search skills..." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-sm" />
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Difficulty</TableHead>
                <TableHead>Categories</TableHead>
                <TableHead>Prerequisites</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground py-8">No skills found</TableCell></TableRow>
              ) : (
                filtered.map((skill) => (
                  <TableRow key={skill.id}>
                    <TableCell className="font-medium">{skill.name}</TableCell>
                    <TableCell><Badge variant="outline">Level {skill.difficulty_level || 1}</Badge></TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {skill.categories?.map((cat) => (
                          <Badge key={cat.id} variant="secondary" className="text-xs">{cat.name}</Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {skill.prerequisites?.length ? skill.prerequisites.map((p) => p.name).join(', ') : 'None'}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(skill.id)} className="text-destructive">
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
