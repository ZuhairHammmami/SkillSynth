'use client';

import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Pencil, Plus } from 'lucide-react';
import { DeleteButton } from '@/components/delete-button';
import { JobRoleDialog } from './job-role-dialog';
import type { JobRole, Skill } from '@/types/api';

/** Admin Job Roles page: role rows with required-skill counts plus
 *  create/edit/delete (delete upgrades 409 conflicts into force-delete). */
export default function JobRolesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<JobRole | undefined>();

  const { data: roles, isLoading } = useQuery<JobRole[]>({
    queryKey: ['jobRoles'],
    queryFn: async () => { const res = await apiClient.get<JobRole[]>('/admin/job-roles'); return res.data; },
  });
  const { data: skills } = useQuery<Skill[]>({
    queryKey: ['skills'],
    queryFn: async () => { const res = await apiClient.get<Skill[]>('/admin/skills'); return res.data; },
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const nameById = new Map((skills || []).map((s) => [s.id, s.name] as [number, string]));
  const filtered = (roles || []).filter(
    (r) => r.title.toLowerCase().includes(search.toLowerCase()) ||
      (r.career_field || '').toLowerCase().includes(search.toLowerCase())
  );

  const openCreate = () => {
    setEditing(undefined);
    setDialogOpen(true);
  };
  const openEdit = (role: JobRole) => {
    setEditing(role);
    setDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Job Roles</h1>
          <p className="text-sm text-muted-foreground mt-1">Career targets the path wizard generates plans for</p>
        </div>
        <Button onClick={openCreate}><Plus className="ms-2 h-4 w-4" />Add Job Role</Button>
      </div>

      <Card>
        <CardHeader>
          <Input placeholder="Search job roles..." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-sm" />
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Career field</TableHead>
                <TableHead>Required skills</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground py-8">No job roles found</TableCell></TableRow>
              ) : (
                filtered.map((role) => (
                  <TableRow key={role.id}>
                    <TableCell className="font-medium">{role.title}</TableCell>
                    <TableCell>{role.career_field ? <Badge variant="outline">{role.career_field}</Badge> : <span className="text-muted-foreground text-sm">—</span>}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {(role.skill_ids || []).length === 0
                        ? 'None'
                        : `${role.skill_ids!.length} mapped — ${(role.skill_ids || []).slice(0, 3).map((id) => nameById.get(id) || `#${id}`).join(', ')}${role.skill_ids!.length > 3 ? ', …' : ''}`}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => openEdit(role)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <DeleteButton
                        endpoint={`/admin/job-roles/${role.id}`}
                        label="job role"
                        queryKeys={['jobRoles', 'wizardOptions']}
                      />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <JobRoleDialog role={editing} open={dialogOpen} onOpenChange={(open) => {
        setDialogOpen(open);
        if (!open) queryClient.invalidateQueries({ queryKey: ['jobRoles'] });
      }} />
    </div>
  );
}