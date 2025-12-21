'use client';

import { useAdminStats } from "@/features/admin/hooks/useAdminStats";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Users, FileText, Activity, Server, TrendingUp, Award } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from 'framer-motion';
import { Badge } from "@/components/ui/badge";

export default function AdminDashboardPage() {
    const { data, isLoading, isError } = useAdminStats();

    if (isLoading) return <DashboardSkeleton />;
    
    if (isError) {
        return (
            <div className="p-8 text-center text-red-500 bg-red-50 rounded-lg border border-red-200">
                فشل تحميل بيانات لوحة التحكم. تأكد من تشغيل الباك اند وصلاحيات الأدمن.
            </div>
        );
    }

    const stats = data!; // نحن متأكدون من وجود البيانات هنا

    return (
        <div className="space-y-8 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">مركز الاستخبارات</h2>
                    <p className="text-muted-foreground">نظرة شاملة على أداء SkillSynth</p>
                </div>
            </div>

            {/* 1. البطاقات العلوية (KPIs) */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <StatsCard 
                    title="إجمالي المستخدمين" 
                    value={stats.userActivity.total_users} 
                    icon={Users} 
                    subtext={`+${stats.userActivity.new_users_last_7d} هذا الأسبوع`}
                />
                <StatsCard 
                    title="المسارات المولدة" 
                    value={stats.contentEngagement.total_paths} 
                    icon={FileText} 
                    subtext="مسار تعليمي مخصص"
                />
                <StatsCard 
                    title="الخطوات المكتملة" 
                    value={stats.contentEngagement.total_completions} 
                    icon={Award} 
                    subtext="خطوة تم إنجازها"
                />
                 <StatsCard 
                    title="حالة النظام" 
                    value={stats.systemHealth.database_status} 
                    icon={Server} 
                    subtext="اتصال قاعدة البيانات"
                    isActive={stats.systemHealth.database_status === 'Connected'}
                />
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                
                {/* 2. جدول المستخدمين الأكثر نشاطاً */}
                <Card className="col-span-4 shadow-sm">
                    <CardHeader>
                        <CardTitle>المستخدمون الأكثر نشاطاً</CardTitle>
                        <CardDescription>أفضل 10 مستخدمين من حيث إنجاز الخطوات</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {stats.mostActiveUsers.length > 0 ? (
                                stats.mostActiveUsers.map((user, i) => (
                                    <div key={i} className="flex items-center justify-between border-b pb-2 last:border-0 last:pb-0">
                                        <div className="flex items-center gap-3">
                                            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                                                {i + 1}
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium leading-none">{user.user_email}</p>
                                            </div>
                                        </div>
                                        <Badge variant="secondary" className="font-mono">
                                            {user.completed_steps} خطوة
                                        </Badge>
                                    </div>
                                ))
                            ) : (
                                <p className="text-sm text-muted-foreground text-center py-4">لا يوجد نشاط كافٍ للعرض.</p>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* 3. المهارات الأكثر طلباً */}
                <Card className="col-span-3 shadow-sm">
                    <CardHeader>
                        <CardTitle>المهارات الأكثر طلباً</CardTitle>
                        <CardDescription>المهارات التي تتكرر في المسارات</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {stats.mostRequestedSkills.length > 0 ? (
                                stats.mostRequestedSkills.map((skill, i) => (
                                    <div key={i} className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <TrendingUp className="h-4 w-4 text-muted-foreground" />
                                            <span className="text-sm font-medium">{skill.skill_name}</span>
                                        </div>
                                        <span className="text-sm text-muted-foreground">{skill.path_count} مسار</span>
                                    </div>
                                ))
                            ) : (
                                <p className="text-sm text-muted-foreground text-center py-4">لا توجد بيانات كافية.</p>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function StatsCard({ title, value, icon: Icon, subtext, isActive }: any) {
    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
                <Icon className={`h-4 w-4 ${isActive === false ? 'text-red-500' : 'text-primary'}`} />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{value}</div>
                <p className={`text-xs ${isActive === false ? 'text-red-500' : 'text-muted-foreground'} mt-1`}>{subtext}</p>
            </CardContent>
        </Card>
    );
}

function DashboardSkeleton() {
    return (
        <div className="p-8 space-y-8">
            <div className="grid gap-4 md:grid-cols-4">
                {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32" />)}
            </div>
            <div className="grid gap-4 md:grid-cols-7">
                <Skeleton className="col-span-4 h-96" />
                <Skeleton className="col-span-3 h-96" />
            </div>
        </div>
    );
}