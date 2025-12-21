// المسار: src/features/wizard/components/Step1_SelectGoal.tsx
'use client';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { WizardOptions } from '@/app/wizard/page'; // <-- المسار صحيح الآن

interface Props {
  options: WizardOptions | null;
  onGoalSelect: (goal: string) => void;
}

export default function Step1_SelectGoal({ options, onGoalSelect }: Props) {
  const [selectedRole, setSelectedRole] = useState<string>('');

  if (!options) {
      return <div className="text-center text-muted-foreground">جاري التحضير...</div>;
  }

  return (
    <div className="space-y-6 flex flex-col items-center">
      <Select onValueChange={setSelectedRole} value={selectedRole}>
        <SelectTrigger className="w-full max-w-sm mx-auto">
          <SelectValue placeholder="اختر هدفك الوظيفي..." />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>الأهداف المتاحة</SelectLabel>
            {options.job_roles.map(role => (
              <SelectItem key={role} value={role}>{role}</SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
      <Button 
        onClick={() => onGoalSelect(selectedRole)} 
        disabled={!selectedRole}
        className="w-full sm:w-auto px-8"
      >
        التالي
      </Button>
    </div>
  );
}