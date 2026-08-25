'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatDate } from '@/lib/utils';
import type { Path } from '@/types/api';

export default function PathsPage() {
  const { data: paths, isLoading } = useQuery<Path[]>({
    queryKey: ['adminPaths'],
    queryFn: async () => { const res = await apiClient.get('/admin/paths'); return res.data; },
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Learning Paths</h1>
        <p className="text-sm text-muted-foreground mt-1">View all learning paths across the platform</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Hours</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paths && paths.length > 0 ? (
                paths.map((path) => (
                  <TableRow key={path.id}>
                    <TableCell className="font-medium">{path.title}</TableCell>
                    <TableCell className="text-muted-foreground">{path.user_email || '—'}</TableCell>
                    <TableCell>{path.total_estimated_hours ?? '—'}h</TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {path.created_at ? formatDate(path.created_at) : '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={path.status === 'active' ? 'success' : 'secondary'}>
                        {path.status || 'active'}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground py-8">No paths found</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
