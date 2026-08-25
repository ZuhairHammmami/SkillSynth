'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, Compass, Activity, TrendingUp, Database } from 'lucide-react';
import type { AdminDashboard } from '@/types/api';

export default function ReportsPage() {
  const { data: dashboard, isLoading } = useQuery<AdminDashboard>({
    queryKey: ['adminReports'],
    queryFn: async () => { const res = await apiClient.get<AdminDashboard>('/admin/reports/aggregated'); return res.data; },
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
        <p className="text-sm text-muted-foreground mt-1">Platform analytics and data reports</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1">
              <Users className="h-4 w-4 text-blue-500" /> Total Users
            </CardTitle>
          </CardHeader>
          <CardContent><div className="text-3xl font-bold">{dashboard?.user_activity?.total_users ?? 0}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1">
              <Compass className="h-4 w-4 text-purple-500" /> Total Paths
            </CardTitle>
          </CardHeader>
          <CardContent><div className="text-3xl font-bold">{dashboard?.content_engagement?.total_paths ?? 0}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1">
              <Activity className="h-4 w-4 text-emerald-500" /> New Users (24h)
            </CardTitle>
          </CardHeader>
          <CardContent><div className="text-3xl font-bold">{dashboard?.user_activity?.new_users_last_24h ?? 0}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1">
              <Database className="h-4 w-4 text-cyan-500" /> DB Status
            </CardTitle>
          </CardHeader>
          <CardContent><div className="text-3xl font-bold">{dashboard?.system_health?.database_status ?? 'unknown'}</div></CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-semibold">
              <TrendingUp className="h-4 w-4 text-emerald-500" /> Platform Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Hours Learned</span>
                <span className="font-medium">{dashboard?.total_hours_learned?.toFixed(1) ?? 0}h</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Completions</span>
                <span className="font-medium">{dashboard?.content_engagement?.total_completions ?? 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Users with Paths</span>
                <span className="font-medium">{dashboard?.user_activity?.users_with_paths ?? 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Avg Completion Rate</span>
                <span className="font-medium">{dashboard?.average_completion_rate ? `${(dashboard.average_completion_rate * 100).toFixed(1)}%` : '0%'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Assessment Attempts</span>
                <span className="font-medium">{dashboard?.total_assessment_attempts ?? 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Avg Assessment Score</span>
                <span className="font-medium">{dashboard?.average_assessment_score ? `${(dashboard.average_assessment_score * 100).toFixed(0)}%` : '0%'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm font-semibold">
              <Users className="h-4 w-4 text-blue-500" /> User Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">New Users (7d)</span>
                <span className="font-medium">{dashboard?.user_activity?.new_users_last_7d ?? 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Users with Paths</span>
                <span className="font-medium">{dashboard?.user_activity?.users_with_paths ?? 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">API Version</span>
                <span className="font-medium">{dashboard?.system_health?.api_version ?? '1.0.0'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Assessments</span>
                <span className="font-medium">{dashboard?.system_health?.total_assessments ?? 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
