'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { CreateSkillDialog } from './create-skill-dialog';
import { EditSkillDialog } from './edit-skill-dialog';
import { DeleteButton } from '@/components/delete-button';
import type { Category, Skill } from '@/types/api';

export default function SkillsPage() {
  const queryClient = useQueryClient();
  const { data: skills, isLoading } = useQuery<Skill[]>({
    queryKey: ['skills'],
    queryFn: async () => { const res = await apiClient.get<Skill[]>('/admin/skills'); return res.data; },
  });
  const { data: categories } = useQuery<Category[]>({
    queryKey: ['adminCategories'],
    queryFn: async () => { const res = await apiClient.get<Category[]>('/admin/categories'); return res.data; },
  });
  const [search, setSearch] = useState('');

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const categoryNameById = new Map((categories || []).map((c) => [c.id, c.name] as [number, string]));
  const skillNameById = new Map((skills || []).map((s) => [s.id, s.name] as [number, string]));
  const filtered = (skills || []).filter((s) => s.name.toLowerCase().includes(search.toLowerCase()));

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
                <TableHead>Category</TableHead>
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
                      {skill.category_id != null ? (
                        <Badge variant="secondary">{categoryNameById.get(skill.category_id) || `#${skill.category_id}`}</Badge>
                      ) : (
                        <span className="text-muted-foreground text-sm">Uncategorized</span>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm max-w-xs truncate">
                      {(skill.prerequisite_ids || []).length === 0
                        ? 'None'
                        : (skill.prerequisite_ids || []).map((id: number) => skillNameById.get(id) || `#${id}`).join(', ')}
                    </TableCell>
                    <TableCell className="text-right">
                      <EditSkillDialog skill={skill} />
                      <DeleteButton
                        endpoint={`/admin/skills/${skill.id}`}
                        label="skill"
                        queryKeys={['skills', 'jobRoles', 'wizardOptions']}
                      />
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