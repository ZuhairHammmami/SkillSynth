'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Download, Database, RefreshCw, HardDrive } from 'lucide-react';
import { useState } from 'react';

interface Backup {
  path: string;
  size_bytes: number;
  size_formatted: string;
  created_at: string;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export default function BackupsPage() {
  const queryClient = useQueryClient();
  const [creating, setCreating] = useState(false);

  const { data: backups, isLoading } = useQuery<Backup[]>({
    queryKey: ['adminBackups'],
    queryFn: async () => { const res = await apiClient.get('/admin/backups'); return res.data; },
  });

  const { data: dbInfo } = useQuery({
    queryKey: ['dbInfo'],
    queryFn: async () => { const res = await apiClient.get('/admin/db-inspector'); return res.data; },
  });

  const createBackup = useMutation({
    mutationFn: async () => {
      setCreating(true);
      const res = await apiClient.post('/admin/backups');
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminBackups'] });
      setCreating(false);
    },
    onError: () => setCreating(false),
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Backups</h1>
          <p className="text-sm text-muted-foreground mt-1">Create and manage database backups</p>
        </div>
        <Button onClick={() => createBackup.mutate()} disabled={creating}>
          <Database className="me-2 h-4 w-4" />
          {creating ? 'Creating...' : 'Create Backup'}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Database Size</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dbInfo?.size_formatted || '—'}</div>
            <p className="text-xs text-muted-foreground mt-1">Current database on disk</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Tables</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dbInfo?.total_tables ?? '—'}</div>
            <p className="text-xs text-muted-foreground mt-1">Database tables</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Backups</CardTitle>
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{backups?.length ?? 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Available backup files</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Backup History</CardTitle>
          <CardDescription>All database backups sorted by creation date</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Filename</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Created At</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!backups || backups.length === 0 ? (
                <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground py-8">No backups created yet</TableCell></TableRow>
              ) : (
                backups.map((backup, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-mono text-sm">{backup.path.replace('backups/', '')}</TableCell>
                    <TableCell>{backup.size_formatted}</TableCell>
                    <TableCell>{new Date(backup.created_at).toLocaleString()}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" asChild>
                        <a href={`/api/admin/backups/download?path=${encodeURIComponent(backup.path)}`} download>
                          <Download className="h-4 w-4" />
                        </a>
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
