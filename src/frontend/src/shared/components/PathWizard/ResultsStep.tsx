'use client';

import { useTranslations } from 'next-intl';
import { Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/shared/ui/card';
import { Badge } from '@/shared/ui/badge';
import { Button } from '@/shared/ui/button';
import type { DiagnosticReport, PerSkillResult } from '@/types/api';

interface ResultsStepProps {
  analysis: DiagnosticReport | null;
  isPending: boolean;
  isError: boolean;
  onContinue: () => void;
}

/** Shape llm_pipeline.analyze_diagnostic actually returns at runtime
 * (the shared DiagnosticReport type narrows narrative to string|null,
 * so this file coerces defensively instead of touching types). */
interface NarrativeShape {
  summary?: string;
  strengths?: { skill?: string; note?: string }[];
  weaknesses?: { skill?: string; reason?: string }[];
  recommended_focus?: string[];
  next_steps?: string;
}

/** Coerce the analysis narrative field into a renderable object.
 * Called by ResultsStep only; accepts object payloads from
 * /wizard/analysis, JSON strings, or falls back to plain-text summary. */
function coerceNarrative(raw: string | null): NarrativeShape | null {
  if (!raw) return null;
  if (typeof raw === 'object') return raw as unknown as NarrativeShape;
  if (typeof raw !== 'string') return null;
  try {
    const parsed: unknown = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') {
      return parsed as NarrativeShape;
    }
  } catch {
    /* plain text */
  }
  return { summary: raw };
}

/** One per-skill diagnostic row. Rendered by ResultsStep; weakness rows
 * get a red start border (flex child, RTL-safe) + gap badge. */
function SkillResultCard({ row }: { row: PerSkillResult }) {
  const t = useTranslations('ai');
  return (
    <Card className="border-border/60">
      <CardContent className="p-3">
        <div className="flex gap-2">
          {row.weakness && (
            <span aria-hidden className="w-1 self-stretch rounded-full bg-red-500 shrink-0" />
          )}
          <div className="flex-1 min-w-0 space-y-1">
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium truncate">{row.skill}</p>
              {row.weakness && (
                <Badge variant="destructive" className="shrink-0">
                  {t('weaknessBadge')}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {t('scoreLabel', { correct: row.correct, total: row.total })}
            </p>
            <p className="text-xs text-muted-foreground">
              {t('levelLabel', { level: row.assessed_level })}
            </p>
            <p className="text-xs text-muted-foreground">
              {t('gapToMastery', { gap: row.gap_to_mastery })}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/** Weaknesses / strengths lists + focus chips under the skill grid.
 * Rendered by ResultsStep; purely deterministic report data. */
function ReportLists({ analysis }: { analysis: DiagnosticReport }) {
  const t = useTranslations('ai');
  return (
    <div className="grid gap-2 sm:grid-cols-2">
      <Card className="border-border/60">
        <CardContent className="p-3 space-y-2">
          <h4 className="text-sm font-semibold">{t('weaknessesTitle')}</h4>
          {analysis.weaknesses.length === 0 ? (
            <p className="text-xs text-muted-foreground">{t('noWeaknesses')}</p>
          ) : (
            analysis.weaknesses.map((w) => (
              <div key={w} className="flex items-center gap-2 text-xs">
                <span className="h-1.5 w-1.5 rounded-full bg-red-500 shrink-0" />
                <span>{w}</span>
              </div>
            ))
          )}
        </CardContent>
      </Card>
      <Card className="border-border/60">
        <CardContent className="p-3 space-y-2">
          <h4 className="text-sm font-semibold">{t('strengthsTitle')}</h4>
          {analysis.strengths.map((s) => (
            <div key={s} className="flex items-center gap-2 text-xs">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
              <span>{s}</span>
            </div>
          ))}
        </CardContent>
      </Card>
      {analysis.recommended_focus.length > 0 && (
        <Card className="border-border/60 sm:col-span-2">
          <CardContent className="p-3 space-y-2">
            <h4 className="text-sm font-semibold">{t('focusTitle')}</h4>
            <div className="flex flex-wrap gap-1.5">
              {analysis.recommended_focus.map((f) => (
                <Badge key={f} variant="outline">{f}</Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/** Optional LLM coach block (summary / next steps / focus chips).
 * Rendered by ResultsStep when narrative_available; tolerates both the
 * documented object payload and a plain-string fallback. */
function NarrativeBlock({ narrative }: { narrative: NarrativeShape }) {
  const t = useTranslations('ai');
  return (
    <Card className="border-primary/20 bg-primary/5">
      <CardContent className="p-4 space-y-3">
        <h4 className="text-sm font-semibold">{t('narrativeTitle')}</h4>
        {narrative.summary && (
          <p className="text-sm text-muted-foreground leading-relaxed">
            {narrative.summary}
          </p>
        )}
        {narrative.next_steps && (
          <div className="space-y-1">
            <p className="text-sm font-medium">{t('nextStepsTitle')}</p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {narrative.next_steps}
            </p>
          </div>
        )}
        {narrative.recommended_focus && narrative.recommended_focus.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {narrative.recommended_focus.map((f) => (
              <Badge key={f} variant="secondary">{f}</Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/** Wizard step 4 (SS-AI two-phase): diagnostic report before path
 * creation. Rendered by PathWizard; consumes POST /wizard/analysis data
 * staged in wizard state and continues to SummaryStep via onContinue.
 * Shows spinner while the analysis mutation is pending and keeps the
 * continue CTA available when the report failed or is deterministic-only. */
export function ResultsStep({ analysis, isPending, isError, onContinue }: ResultsStepProps) {
  const t = useTranslations('ai');

  if (isPending) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-10">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">{t('analyzing')}</p>
      </div>
    );
  }

  const narrative = analysis ? coerceNarrative(analysis.narrative) : null;

  return (
    <div className="space-y-4 py-2">
      {isError || !analysis ? (
        <p className="text-sm text-destructive text-center py-4">{t('analysisFailed')}</p>
      ) : (
        <>
          <p className="text-xs text-muted-foreground">
            {t('estimatedWeeks', { weeks: analysis.estimated_weeks })}
          </p>
          <div className="grid gap-2 sm:grid-cols-2">
            {analysis.per_skill.map((row) => (
              <SkillResultCard key={row.skill_id} row={row} />
            ))}
          </div>
          <ReportLists analysis={analysis} />
          {analysis.narrative_available && narrative && (
            <NarrativeBlock narrative={narrative} />
          )}
        </>
      )}
      <Button className="w-full" onClick={onContinue}>
        {t('continueToSummary')}
      </Button>
    </div>
  );
}
