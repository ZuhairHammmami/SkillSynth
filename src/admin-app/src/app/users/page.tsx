'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { CreateUserDialog } from './create-user-dialog';
import { EditUserDialog } from './edit-user-dialog';
import { DeleteButton } from '@/components/delete-button';
import type { Profile } from '@/types/api';

export default function UsersPage() {
  const { data: users, isLoading } = useQuery<Profile[]>({
    queryKey: ['adminUsers'],
    queryFn: async () => { const res = await apiClient.get<Profile[]>('/admin/users'); return res.data; },
  });
  const [search, setSearch] = useState('');

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const filtered = (users || []).filter(
    (u) => u.email.toLowerCase().includes(search.toLowerCase()) ||
      (u.full_name || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Users</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage platform users</p>
        </div>
        <CreateUserDialog />
      </div>
      <Card>
        <CardHeader>
          <Input placeholder="Search users..." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-sm" />
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground py-8">No users found</TableCell></TableRow>
              ) : (
                filtered.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.full_name || '—'}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell><Badge variant={user.is_admin ? 'default' : 'secondary'}>{user.is_admin ? 'Admin' : 'User'}</Badge></TableCell>
                    <TableCell className="text-right">
                      <EditUserDialog user={user} />
                      <DeleteButton
                        endpoint={`/admin/users/${user.id}`}
                        label="user"
                        queryKeys={['adminUsers']}
                        confirmText="Delete this user? Their paths, progress and assessment results are removed too."
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
