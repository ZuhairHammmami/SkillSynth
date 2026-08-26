'use client';

import { useTranslations } from 'next-intl';
import { Label } from '@/shared/ui/label';
import { Slider } from '@/shared/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select';
import { RadioGroup, RadioGroupItem } from '@/shared/ui/radio-group';
import { Card, CardContent } from '@/shared/ui/card';
import { BookOpen, Check, Clock } from 'lucide-react';
import { FORMATS, LANGUAGES, LEVELS } from './types';

interface PreferencesStepProps {
  skillLevel: string;
  weeklyHours: number;
  format: string;
  language: string;
  freeContentOnly: boolean;
  onSkillLevelChange: (v: string) => void;
  onHoursChange: (v: number) => void;
  onFormatChange: (v: string) => void;
  onLanguageChange: (v: string) => void;
  onFreeContentToggle: () => void;
}

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function PreferencesStep({
  skillLevel, weeklyHours, format, language, freeContentOnly,
  onSkillLevelChange, onHoursChange, onFormatChange, onLanguageChange, onFreeContentToggle,
}: PreferencesStepProps) {
  const t = useTranslations('wizard');

  return (
    <div className="space-y-5">
      <div className="space-y-3">
        <Label>{t('levelTitle')}</Label>
        <p className="text-xs text-muted-foreground">{t('levelSubtitle')}</p>
        <RadioGroup value={skillLevel} onValueChange={onSkillLevelChange} className="grid grid-cols-2 gap-3">
          {LEVELS.map((lvl) => {
            const isSelected = skillLevel === lvl;
            return (
              <div key={lvl}>
                <RadioGroupItem value={lvl} id={`lvl-${lvl}`} className="peer sr-only" />
                <Label htmlFor={`lvl-${lvl}`} className="cursor-pointer">
                  <Card
                    className={`transition-all ${
                      isSelected ? 'border-primary ring-1 ring-primary' : 'border-border'
                    }`}
                  >
                    <CardContent className="p-4 space-y-1">
                      <div className="flex items-center gap-2">
                        <BookOpen className={`h-4 w-4 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`} />
                        <span className="font-medium text-sm">{t(`level${capitalize(lvl)}`)}</span>
                        {isSelected && <Check className="h-3.5 w-3.5 ms-auto text-primary shrink-0" />}
                      </div>
                      <p className="text-xs text-muted-foreground">{t(`level${capitalize(lvl)}Desc`)}</p>
                    </CardContent>
                  </Card>
                </Label>
              </div>
            );
          })}
        </RadioGroup>
      </div>

      <div className="space-y-3">
        <Label>{t('weeklyHours')}</Label>
        <div className="flex items-center gap-4">
          <Slider
            value={[weeklyHours]}
            onValueChange={([v]) => onHoursChange(v)}
            min={5}
            max={40}
            step={5}
            className="flex-1"
          />
          <div className="flex items-center gap-1 min-w-[4rem]">
            <Clock className="h-4 w-4 text-muted-foreground shrink-0" />
            <span className="text-sm font-medium tabular-nums">{weeklyHours}h</span>
          </div>
        </div>
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>5h</span>
          <span>40h</span>
        </div>
      </div>

      <div className="space-y-2">
        <Label>{t('formatLabel')}</Label>
        <Select value={format} onValueChange={onFormatChange}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {FORMATS.map((fmt) => (
              <SelectItem key={fmt} value={fmt}>
                {t(`format${capitalize(fmt)}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>{t('languageLabel')}</Label>
        <Select value={language} onValueChange={onLanguageChange}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {LANGUAGES.map((lang) => (
              <SelectItem key={lang} value={lang}>
                {t(`language${lang.toUpperCase()}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <label className="flex items-center gap-3 cursor-pointer">
        <button
          type="button"
          role="switch"
          aria-checked={freeContentOnly}
          onClick={onFreeContentToggle}
          className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${
            freeContentOnly ? 'bg-primary' : 'bg-input'
          }`}
        >
          <span
            className={`pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform ${
              freeContentOnly ? 'translate-x-4' : 'translate-x-0'
            }`}
          />
        </button>
        <div className="space-y-0.5">
          <span className="text-sm font-medium leading-none">{t('freeContentLabel')}</span>
          <p className="text-xs text-muted-foreground">{t('freeContentDesc')}</p>
        </div>
      </label>
    </div>
  );
}
