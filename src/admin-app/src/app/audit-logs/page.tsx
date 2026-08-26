'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import type { Event } from '@/types/api';

export default function AuditLogsPage() {
  const { data: events, isLoading } = useQuery<Event[]>({
    queryKey: ['auditLog'],
    queryFn: async () => { const res = await apiClient.get<Event[]>('/admin/events'); return res.data; },
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'audit': return 'default' as const;
      case 'auth': return 'warning' as const;
      case 'system': return 'success' as const;
      default: return 'secondary' as const;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Audit Logs</h1>
        <p className="text-sm text-muted-foreground mt-1">View the audit trail of system events</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Entity</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {events && events.length > 0 ? (
                events.map((ev) => (
                  <TableRow key={ev.id}>
                    <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                      {ev.created_at ? new Date(ev.created_at).toLocaleString() : '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getCategoryColor(ev.category)}>{ev.category}</Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{ev.action}</TableCell>
                    <TableCell className="text-sm">
                      {ev.user?.email || `User #${ev.profile_id}` || 'System'}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {ev.entity_type ? `${ev.entity_type}#${ev.entity_id}` : '—'}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground py-8">No events found</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
