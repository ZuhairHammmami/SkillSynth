import { useQuery } from '@tanstack/react-query';
import apiClient from '@/shared/lib/api';

// تعريف الواجهات بناءً على التوثيق الذي أرسلته
interface UserActivityReport {
  total_users: number;
  new_users_last_24h: number;
  new_users_last_7d: number;
  users_with_paths: number;
}

interface ContentEngagementReport {
  total_paths: number;
  total_steps: number;
  total_completions: number;
}

interface SystemHealthReport {
  database_status: string;
}

interface ActiveUser {
  user_email: string;
  completed_steps: number;
}

interface RequestedSkill {
  skill_name: string;
  path_count: number;
}

// الواجهة المجمعة التي ستستخدمها الصفحة
export interface AdminDashboardData {
  userActivity: UserActivityReport;
  contentEngagement: ContentEngagementReport;
  systemHealth: SystemHealthReport;
  mostActiveUsers: ActiveUser[];
  mostRequestedSkills: RequestedSkill[];
}

const fetchAdminDashboardData = async (): Promise<AdminDashboardData> => {
  // جلب جميع التقارير بشكل متوازي
  const [userActivity, contentEngagement, systemHealth, activeUsers, requestedSkills] = await Promise.all([
    apiClient.get<UserActivityReport>('/api/admin/reports/user-activity'),
    apiClient.get<ContentEngagementReport>('/api/admin/reports/content-engagement'),
    apiClient.get<SystemHealthReport>('/api/admin/reports/system-health'),
    apiClient.get<ActiveUser[]>('/api/admin/reports/most-active-users'),
    apiClient.get<RequestedSkill[]>('/api/admin/reports/most-requested-skills'),
  ]);

  return {
    userActivity: userActivity.data,
    contentEngagement: contentEngagement.data,
    systemHealth: systemHealth.data,
    mostActiveUsers: activeUsers.data,
    mostRequestedSkills: requestedSkills.data,
  };
};

export const useAdminStats = () => {
  return useQuery({
    queryKey: ['admin-dashboard-stats'],
    queryFn: fetchAdminDashboardData,
    staleTime: 1000 * 60 * 5, // تحديث كل 5 دقائق
  });
};