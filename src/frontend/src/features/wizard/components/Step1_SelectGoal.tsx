'use client';
import { useState } from 'react';
import { Button } from '@/shared/ui/button';
import { motion } from 'framer-motion';
import { Briefcase, ChevronLeft } from 'lucide-react';
import type { WizardOptions } from '@/app/wizard/page';

interface Props {
  options: WizardOptions | null;
  onGoalSelect: (goal: string) => void;
}

export default function Step1_SelectGoal({ options, onGoalSelect }: Props) {
  const [selectedRole, setSelectedRole] = useState<string>('');

  if (!options) return null;

  return (
    <div className="space-y-8 text-center">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-primary">ما هو هدفك المهني القادم؟</h2>
        <p className="text-muted-foreground">اختر المسار الذي تطمح للوصول إليه لنقوم بتخصيص الخطة لك.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
        {options.job_roles.map((role, index) => (
            <motion.div
                key={role}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
            >
                <div 
                    onClick={() => setSelectedRole(role)}
                    className={`
                        cursor-pointer p-4 rounded-xl border-2 transition-all duration-200 flex items-center gap-3
                        ${selectedRole === role 
                            ? 'border-primary bg-primary/5 shadow-md ring-2 ring-primary/20' 
                            : 'border-border hover:border-primary/50 hover:bg-muted/30'}
                    `}
                >
                    <div className={`p-2 rounded-full ${selectedRole === role ? 'bg-primary text-white' : 'bg-muted text-muted-foreground'}`}>
                        <Briefcase className="w-5 h-5" />
                    </div>
                    <span className="font-semibold text-lg">{role}</span>
                </div>
            </motion.div>
        ))}
      </div>

      <div className="pt-6 flex justify-end">
        <Button 
            onClick={() => onGoalSelect(selectedRole)} 
            disabled={!selectedRole}
            size="lg"
            className="gap-2 px-8"
        >
            التالي
            <ChevronLeft className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}