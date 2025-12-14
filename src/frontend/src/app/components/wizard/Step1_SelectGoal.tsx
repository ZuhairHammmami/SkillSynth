// المسار: src/app/components/wizard/Step1_SelectGoal.tsx
'use client';
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Props {
  onGoalSelect: (goal: string) => void;
}

export default function Step1_SelectGoal({ onGoalSelect }: Props) {
  const [roles, setRoles] = useState<string[]>([]);
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiClient.get<{ job_roles: string[] }>('/api/wizard-options')
      .then(res => setRoles(res.data.job_roles))
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <p>جارٍ تحميل الخيارات...</p>;

  return (
    <div className="space-y-6 flex flex-col items-center">
      <Select onValueChange={setSelectedRole} value={selectedRole}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="اختر هدفك الوظيفي..." />
        </SelectTrigger>
        <SelectContent>
          {roles.map(role => <SelectItem key={role} value={role}>{role}</SelectItem>)}
        </SelectContent>
      </Select>
      <Button onClick={() => onGoalSelect(selectedRole)} disabled={!selectedRole}>
        ابدأ اختبار تحديد المستوى
      </Button>
    </div>
  );
}