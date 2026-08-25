# SS-EDS: Accessibility

## Purpose
Document the accessibility strategy for SkillSynth: WCAG 2.1 AA targets on the current light-theme token system, RTL screen-reader support, keyboard navigation, color contrast (computed from globals.css tokens), and touch targets.

## Responsibilities
- Keep all interactive elements keyboard accessible with visible focus rings
- Maintain semantic HTML + ARIA alignment
- Enforce contrast ratios from the HSL tokens in `src/frontend/src/app/globals.css`
- Standardize touch-target sizing

## Inputs
- WCAG 2.1 AA guidelines
- Design tokens (20-ui-system)
- RTL typography behavior (Tajawal)

## Outputs
- Contrast matrix (this document, computed from tokens)
- ARIA/label conventions for forms and icon buttons

## Dependencies
- 20-ui-system (token values)
- 08-frontend (component implementation)
- 00-principles (RTL-first commitment)

## Sequence: Accessibility Audit Flow
```
Page → Lighthouse a11y scan → manual keyboard pass → screen-reader spot check → fix → re-scan
```

## State Diagram: Compliance
```
[Not Compliant] → [Partial] → [WCAG AA] → [AAA (future goal)]
```

## Color Contrast (computed from current tokens; background = white `--background`)
| Foreground | Token | Ratio vs white | WCAG |
|------------|-------|----------------|------|
| Primary text | `--foreground` (240 10% 3.9%) | 20.0:1 | AA + AAA |
| Secondary text | `--muted-foreground` (215.4 16.3% 46.9%) | 4.8:1 | AA (normal text) |
| Brand/actions | `--primary` (221 83% 53%) | 5.2:1 | AA (normal text) |
| Text on primary | `--primary-foreground` on `--primary` | 5.0:1 | AA (normal text) |
| Error text/large UI | `--destructive` (0 84.2% 60.2%) | 3.8:1 | AA large text / UI components |

Focus indication uses `--ring` (= `--primary`) via the standard `ring-2 ring-ring` pattern.

## Keyboard Navigation
| Input | Action |
|-------|--------|
| Tab / Shift+Tab | Cycle focus through interactive elements in DOM order |
| Enter / Space | Activate buttons, links, form controls |
| Escape | Close dialogs and popovers (shadcn/ui default) |
| Arrow keys | Navigate menus, radio groups, and the category tree |

## ERD References
- None — accessibility has no dedicated persistence

## Rules
1. Every interactive element is reachable and operable by keyboard
2. Every image carries alt text; every input has an associated `<label>`
3. Color never encodes meaning alone — pair icons/text with state colors
4. Touch/click targets ≥44×44px (48px preferred)
5. Focus rings are always visible (`ring-2 ring-ring`); never removed without replacement
6. RTL: logical properties (`ms-/me-/ps-/pe-`) so mirroring never breaks hit areas

## Examples
- Login form: `<label htmlFor="email">{t('auth.email')}</label>` bound to the input
- Icon-only button: `aria-label={t('common.close')}` with visible focus ring

## Edge Cases
- Mixed RTL/LTR content (code snippets in Arabic UI) — isolate directionality per block
- Chart/diagram content needs text alternatives or accessible summaries

## Failure Cases
- Missing aria-label on icon-only button → audit failure
- New token pairing under 4.5:1 for body text → rejected at review

## Recovery Procedures
1. Run Lighthouse accessibility category; address flagged items
2. Re-verify computed ratios after any token change (see table above)

## Refactoring Strategy
- Add automated axe-core checks to CI
- Dark mode would invert tokens — recompute this matrix before shipping it
