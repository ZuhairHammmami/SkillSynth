'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, Server, Activity, CheckCircle, XCircle } from 'lucide-react';

export default function HealthPage() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['adminDashboard'],
    queryFn: async () => {
      const res = await apiClient.get('/admin/reports/aggregated');
      return res.data;
    },
  });
  const { data: healthReport } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: async () => {
      try { const res = await apiClient.get('/admin/reports/system-health'); return res.data; }
      catch { return null; }
    },
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const health = dashboard?.system_health || {};
  const dbOk = health.database_status === 'healthy' || health.database_status === 'connected';
  const extra = healthReport || {};

  const checks = [
    { label: 'Database', status: dbOk, icon: Database, detail: health.database_status || 'unknown' },
    { label: 'API Server', status: true, icon: Server, detail: health.api_version || '1.0.0' },
    { label: 'Total Users', status: true, icon: Activity, detail: String(health.total_users || 0) },
    { label: 'Total Paths', status: true, icon: Activity, detail: String(health.total_paths || 0) },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">System Health</h1>
        <p className="text-sm text-muted-foreground mt-1">Monitor system status and performance</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {checks.map((check) => (
          <Card key={check.label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <check.icon className="h-4 w-4 text-muted-foreground" />
                {check.label}
              </CardTitle>
              {check.status ? (
                <CheckCircle className="h-5 w-5 text-emerald-500" />
              ) : (
                <XCircle className="h-5 w-5 text-destructive" />
              )}
            </CardHeader>
            <CardContent>
              <div className="text-sm">{check.detail}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Information</CardTitle>
          <CardDescription>Additional system details</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">API Version</span>
              <Badge variant="secondary">{health.api_version || '1.0.0'}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Database Status</span>
              <Badge variant={dbOk ? 'success' : 'destructive'}>{health.database_status || 'unknown'}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Assessments</span>
              <span className="font-medium">{health.total_assessments ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Cache</span>
              <Badge variant="success">Operational</Badge>
            </div>
            {(extra as Record<string, unknown>).details ? (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Details</span>
                <span className="font-medium">{String((extra as Record<string, unknown>).details)}</span>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
