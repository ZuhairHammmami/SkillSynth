# SS-EDS: Principles

## Purpose
Define the foundational design principles, philosophy, and architectural axioms that guide all decisions across the SkillSynth Adaptive Learning OS.

## Responsibilities
- Establish non-negotiable design axioms
- Document RTL-first, Arabic-first localization commitments
- Define the modular synthesizer metaphor as the UX paradigm
- Enforce flat/solid color design tokens with zero gradients

## Inputs
- Product vision documents
- Stakeholder requirements
- Accessibility standards (WCAG 2.1 AA)
- RTL typography research

## Outputs
- Design token specification
- Axiom validation checklist
- Metaphor purity guidelines (term replacements)

## Dependencies
- 01-product (product goals inform principles)
- 20-ui-system (tokens derived from principles)
- 21-accessibility (principles must align with WCAG)

## Sequence: Principle Enforcement Flow
```
PRD → Principle Review Board → Principle Violation? → Yes → Reject / Redesign
                                                      ↓  No
                                              Architecture Decision
                                                      ↓
                                              Implementation
                                                      ↓
                                              Audit (Lighthouse / a11y)
```

## State Diagram: Principle Lifecycle
```
[Draft] → [Reviewed] → [Approved] → [Active] → [Deprecated]
    ↑                        ↓                         ↓
    └──── Revision ──────────┘            [Superseded / Removed]
```

## ERD References
- docs/40-diagrams/ for token dependency graphs

## Rules
1. No gradients anywhere — flat solid colors only
2. No border-radius > 2px on containers (50% only on knobs)
3. RTL-first: html lang="ar" dir="rtl" is default
4. Tajawal font for body, IBM Plex Sans for headings
5. All user-facing text must be i18n'd (en/ar)
6. No HttpOnly cookie for JWT (known risk, intentional)

## Examples
- `--bg-root: #0B0B0D` as infinite workspace background
- Term replacements: "Login" → "Signal Tuning", "Button" → "Knob"

## Edge Cases
- Mixed RTL/LTR content in same view (e.g., code blocks in Arabic UI)
- Screen reader handling of synth metaphor terminology
- Colorblind accessibility with teal/brass/success/danger palette

## Failure Cases
- Principle violation discovered during code review → block merge
- WCAG AA failure due to insufficient contrast on brass (#D4A843 on #16161A)

## Recovery Procedures
1. Log violation in decision record (docs/41-decision-records/)
2. File issue with principle override rationale
3. Update principle if override is accepted

## Refactoring Strategy
- Principles change only through formal RFC
- Track principle adoption rate via audit scripts
- Review principles quarterly against product evolution
