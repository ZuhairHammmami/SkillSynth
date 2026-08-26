'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Trash2 } from 'lucide-react';
import type { Assessment } from '@/types/api';

export default function AssessmentsPage() {
  const { data: assessments, isLoading } = useQuery<Assessment[]>({
    queryKey: ['adminAssessments'],
    queryFn: async () => { const res = await apiClient.get<Assessment[]>('/admin/assessments'); return res.data; },
  });
  const queryClient = useQueryClient();
  const deleteAssessment = useMutation({
    mutationFn: async (id: number) => { await apiClient.delete(`/admin/assessments/${id}`); },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['adminAssessments'] }),
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Assessments</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage assessments and view results</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Passing Score</TableHead>
                <TableHead>Time Limit</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {assessments && assessments.length > 0 ? (
                assessments.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="font-medium">{a.title}</TableCell>
                    <TableCell><Badge variant="secondary">{a.assessment_type}</Badge></TableCell>
                    <TableCell>{a.passing_score ?? 70}%</TableCell>
                    <TableCell>{a.time_limit_minutes ? `${a.time_limit_minutes}m` : '—'}</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => deleteAssessment.mutate(a.id)} className="text-destructive">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground py-8">No assessments found</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
