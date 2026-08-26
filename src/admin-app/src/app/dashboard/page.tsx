'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, BookOpen, Compass, Activity, Database, TrendingUp } from 'lucide-react';
import type { AdminDashboard } from '@/types/api';

function PageLoading() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { data: dashboard, isLoading } = useQuery<AdminDashboard>({
    queryKey: ['adminDashboard'],
    queryFn: async () => {
      const res = await apiClient.get<AdminDashboard>('/admin/reports/aggregated');
      return res.data;
    },
  });

  if (isLoading) return <PageLoading />;

  const stats = [
    { label: 'Total Users', value: dashboard?.user_activity?.total_users ?? 0, icon: Users, color: 'text-blue-600' },
    { label: 'Active (24h)', value: dashboard?.user_activity?.new_users_last_24h ?? 0, icon: Activity, color: 'text-emerald-600' },
    { label: 'Total Paths', value: dashboard?.content_engagement?.total_paths ?? 0, icon: Compass, color: 'text-purple-600' },
    { label: 'Completions', value: dashboard?.content_engagement?.total_completions ?? 0, icon: TrendingUp, color: 'text-orange-600' },
    { label: 'Total Skills', value: dashboard?.most_requested_skills?.length ?? 0, icon: BookOpen, color: 'text-indigo-600' },
    { label: 'DB Status', value: dashboard?.system_health?.database_status ?? 'unknown', icon: Database, color: 'text-cyan-600' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Overview of the SkillSynth platform</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Most Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            {dashboard?.most_active_users && dashboard.most_active_users.length > 0 ? (
              <div className="space-y-3">
                {dashboard.most_active_users.slice(0, 5).map((user, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span>{user.user_email}</span>
                    <span className="text-muted-foreground">{user.completed_steps} steps</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No activity data available</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Most Requested Skills</CardTitle>
          </CardHeader>
          <CardContent>
            {dashboard?.most_requested_skills && dashboard.most_requested_skills.length > 0 ? (
              <div className="space-y-3">
                {dashboard.most_requested_skills.slice(0, 5).map((skill, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span>{skill.skill_name}</span>
                    <span className="text-muted-foreground">{skill.path_count} paths</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No skill data available</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Additional Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Hours Learned</span>
                <span className="font-medium">{dashboard?.total_hours_learned?.toFixed(1) ?? 0}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Avg Completion Rate</span>
                <span className="font-medium">{dashboard?.average_completion_rate ? `${(dashboard.average_completion_rate * 100).toFixed(1)}%` : '0%'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Assessment Attempts</span>
                <span className="font-medium">{dashboard?.total_assessment_attempts ?? 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Avg Assessment Score</span>
                <span className="font-medium">{dashboard?.average_assessment_score ? `${(dashboard.average_assessment_score * 100).toFixed(0)}%` : '0%'}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
