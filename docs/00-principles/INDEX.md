# SS-EDS: Principles

## Purpose
Define the foundational design principles and architectural axioms that guide all decisions across the SkillSynth adaptive learning platform: a professional Linear/Notion-style aesthetic, RTL-first bilingual delivery, and Clean Architecture discipline.

## Responsibilities
- Establish non-negotiable design axioms
- Document RTL-first, Arabic-default localization commitments
- Enforce flat/solid color design tokens — no gradients
- Enforce layering and file-size discipline in all code

## Inputs
- Product goals (01-product)
- Accessibility standards (WCAG 2.1 AA)
- RTL typography research (Tajawal)

## Outputs
- Design token specification (20-ui-system)
- Principle checklist applied in code review

## Dependencies
- 01-product (product goals inform principles)
- 20-ui-system (tokens derived from principles)
- 21-accessibility (principles must align with WCAG)

## Sequence: Principle Enforcement Flow
```
Change → PR Review → Principle violation? → Yes → Reject / Redesign
                                            ↓  No
                                     Merge → Audit (Lighthouse / a11y)
```

## State Diagram: Principle Lifecycle
```
[Draft] → [Reviewed] → [Approved] → [Active] → [Superseded]
    ↑                        ↓
    └──── Revision ──────────┘
```

## ERD References
- None (principles are non-persistent); diagrams live in docs/40-diagrams/

## Rules
1. No gradients, neon, glassmorphism, or heavy shadows — flat solid colors only
2. Visual language follows Linear/Notion/Stripe: neutral surfaces, restrained accent (`--primary` blue), subtle borders
3. RTL-first: `<html lang="ar" dir="rtl">` is the default document direction; Tajawal is the primary typeface
4. All user-facing text must use i18n message keys (ar/en) — zero hardcoded strings
5. Backend layering: Router → Service → Repository → Entity; imports as `from backend.xxx import yyy`
6. No file > 300 lines, no function > 40 lines; every function carries a docstring stating its purpose and callers/callees

## Examples
- Button: solid `--primary` background, `rounded-md`, visible focus ring — no glow or gradient
- A new endpoint lands in a router only if it delegates immediately to a service

## Edge Cases
- Mixed RTL/LTR content in the same view (code blocks inside Arabic UI) — use logical CSS properties
- English-only admin app (09-admin) still follows the same token system

## Failure Cases
- Principle violation found in review → block merge until resolved
- WCAG AA failure from a new color pairing → fix tokens before merge

## Recovery Procedures
1. Record the exception rationale in a decision record (docs/41-decision-records/)
2. Update this principle if the override is accepted

## Refactoring Strategy
- Principles change only through a documented decision record
- Re-audit contrast and Lighthouse scores on every UI change
