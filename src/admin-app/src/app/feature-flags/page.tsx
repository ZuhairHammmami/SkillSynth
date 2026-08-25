'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ToggleLeft, Shield, Key, Globe, Clock, Lock, AlertTriangle } from 'lucide-react';

interface PasswordPolicy {
  min_length: number;
  require_uppercase: boolean;
  require_lowercase: boolean;
  require_digit: boolean;
  require_special_char: boolean;
}

interface FeatureFlagsData {
  app_mode: string;
  registration_enabled: boolean;
  ai_path_generation: boolean;
  real_time_updates: boolean;
  csrf_protection: boolean;
  rate_limiting: boolean;
  password_policy: PasswordPolicy;
  session_timeout_hours: number;
  account_lockout_attempts: number;
  cors_origins: string[];
}

export default function FeatureFlagsPage() {
  const { data, isLoading } = useQuery<FeatureFlagsData>({
    queryKey: ['featureFlags'],
    queryFn: async () => { const res = await apiClient.get('/admin/feature-flags'); return res.data; },
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const features = [
    { label: 'App Mode', value: data?.app_mode || '—', icon: Globe, badge: true, badgeVariant: data?.app_mode === 'prod' ? 'success' : 'warning' },
    { label: 'Registration', value: data?.registration_enabled ? 'Enabled' : 'Disabled', icon: ToggleLeft, badge: true, badgeVariant: data?.registration_enabled ? 'success' : 'secondary' },
    { label: 'AI Path Generation', value: data?.ai_path_generation ? 'Enabled' : 'Disabled', icon: ToggleLeft, badge: true, badgeVariant: data?.ai_path_generation ? 'success' : 'secondary' },
    { label: 'Real-time Updates', value: data?.real_time_updates ? 'Enabled' : 'Disabled', icon: ToggleLeft, badge: true, badgeVariant: data?.real_time_updates ? 'success' : 'secondary' },
    { label: 'CSRF Protection', value: data?.csrf_protection ? 'Enabled' : 'Disabled', icon: Shield, badge: true, badgeVariant: data?.csrf_protection ? 'success' : 'destructive' },
    { label: 'Rate Limiting', value: data?.rate_limiting ? 'Enabled' : 'Disabled', icon: AlertTriangle, badge: true, badgeVariant: data?.rate_limiting ? 'success' : 'destructive' },
    { label: 'Session Timeout', value: `${data?.session_timeout_hours ?? 24}h`, icon: Clock, badge: false },
    { label: 'Account Lockout', value: `${data?.account_lockout_attempts ?? 5} attempts`, icon: Lock, badge: false },
  ];

  const policyItems = data?.password_policy ? [
    { label: 'Min Length', value: String(data.password_policy.min_length) },
    { label: 'Uppercase Required', value: data.password_policy.require_uppercase ? 'Yes' : 'No' },
    { label: 'Lowercase Required', value: data.password_policy.require_lowercase ? 'Yes' : 'No' },
    { label: 'Digit Required', value: data.password_policy.require_digit ? 'Yes' : 'No' },
    { label: 'Special Char Required', value: data.password_policy.require_special_char ? 'Yes' : 'No' },
  ] : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">System Configuration</h1>
        <p className="text-sm text-muted-foreground mt-1">Read-only view of system configuration, security settings, and feature toggles</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {features.map((f) => (
          <Card key={f.label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <f.icon className="h-4 w-4 text-muted-foreground" />
                {f.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {f.badge ? (
                <Badge variant={f.badgeVariant as 'success' | 'warning' | 'secondary' | 'destructive'}>{String(f.value)}</Badge>
              ) : (
                <div className="text-lg font-bold">{String(f.value)}</div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Password Policy</CardTitle>
          <CardDescription>Authentication security requirements</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule</TableHead>
                <TableHead>Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {policyItems.map((item) => (
                <TableRow key={item.label}>
                  <TableCell className="font-medium">{item.label}</TableCell>
                  <TableCell>
                    <Badge variant={item.value === 'Yes' ? 'success' : item.value === 'No' ? 'destructive' : 'secondary'}>
                      {item.value}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>CORS Origins</CardTitle>
          <CardDescription>Allowed cross-origin request sources</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {(data?.cors_origins || []).length === 0 ? (
              <p className="text-sm text-muted-foreground">No CORS origins configured</p>
            ) : (
              (data?.cors_origins || []).map((origin, idx) => (
                <div key={idx} className="flex items-center gap-2 rounded-md bg-muted px-3 py-2 text-sm font-mono">
                  <Globe className="h-3.5 w-3.5 text-muted-foreground" />
                  {origin}
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
