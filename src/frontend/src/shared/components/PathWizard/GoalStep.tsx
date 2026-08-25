'use client';

import { useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { Sparkles, Check } from 'lucide-react';
import { Card, CardContent } from '@/shared/ui/card';
import { Combobox } from '@/shared/ui/combobox';
import { ROLE_COLORS } from './types';

interface GoalStepProps {
  roles: { title: string; career_field: string }[] | undefined;
  selectedRole: { title: string; career_field: string } | null;
  onSelect: (role: { title: string; career_field: string }) => void;
  onClearSearch: () => void;
}

export function GoalStep({ roles, selectedRole, onSelect, onClearSearch }: GoalStepProps) {
  const t = useTranslations('wizard');

  const topRoles = (roles ?? []).slice(0, 6);

  const comboboxOptions = useMemo(() => (
    (roles ?? []).map((r) => ({
      value: r.title,
      label: r.title,
      subtitle: r.career_field,
    }))
  ), [roles]);

  const handleComboboxSelect = (title: string) => {
    const role = (roles ?? []).find((r) => r.title === title);
    if (role) {
      onSelect(role);
      onClearSearch();
    }
  };

  return (
    <div className="space-y-4">
      <Combobox
        options={comboboxOptions}
        value={selectedRole?.title ?? ''}
        onSelect={handleComboboxSelect}
        placeholder={t('searchRoles')}
        emptyText={t('noResults')}
        className="w-full"
      />

      {!selectedRole && (
        <>
          <p className="text-sm font-medium text-muted-foreground mb-2">{t('popularRoles')}</p>
          <div className="grid grid-cols-2 gap-2">
            {topRoles.map((role, i) => {
              const color = ROLE_COLORS[i % ROLE_COLORS.length];
              return (
                <button
                  key={role.title}
                  type="button"
                  onClick={() => onSelect(role)}
                  className="w-full text-start"
                >
                  <Card
                    className={`transition-all hover:border-muted-foreground/30`}
                  >
                    <CardContent className="p-3">
                      <div className={`inline-flex items-center justify-center h-8 w-8 rounded-lg ${color.bg} ${color.text} mb-2`}>
                        <Sparkles className="h-4 w-4" />
                      </div>
                      <p className="text-sm font-medium leading-tight">{role.title}</p>
                      {role.career_field && (
                        <p className="text-xs text-muted-foreground mt-0.5">{role.career_field}</p>
                      )}
                    </CardContent>
                  </Card>
                </button>
              );
            })}
          </div>
        </>
      )}

      {selectedRole && (
        <div className="flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 p-2 text-sm">
          <Check className="h-4 w-4 text-primary shrink-0" />
          <span className="font-medium">{selectedRole.title}</span>
          {selectedRole.career_field && (
            <span className="text-xs text-muted-foreground ms-auto">{selectedRole.career_field}</span>
          )}
        </div>
      )}
    </div>
  );
}
