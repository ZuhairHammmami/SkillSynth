# SS-EDS: Accessibility

## Purpose
Document the accessibility strategy for SkillSynth, covering WCAG 2.1 AA compliance, RTL screen reader support, keyboard navigation, color contrast, and touch targets.

## Responsibilities
- Ensure WCAG 2.1 AA compliance across all pages
- Maintain proper ARIA attributes and roles
- Implement keyboard navigation for all interactive elements
- Ensure sufficient color contrast ratios
- Provide touch-accessible interaction patterns

## Inputs
- WCAG 2.1 AA guidelines
- RTL accessibility research
- Color contrast analysis

## Outputs
- Accessibility audit reports
- Keyboard navigation specification
- ARIA label inventory
- Touch target size definitions

## Dependencies
- 20-ui-system (design tokens, component states)
- 08-frontend (component implementation)
- 00-principles (RTL-first commitment)

## Sequence: Accessibility Audit Flow
```
Page Load → Automated Scan (Lighthouse) → Manual ARIA Review → Keyboard Navigation Test → Screen Reader Test → Report → Fix Issues
```

## State Diagram: Accessibility Compliance
```
[Not Compliant] → [Partial] → [WCAG AA Compliant] → [WCAG AAA (Future)]
```

## Color Contrast (Key Pairs)
| Foreground | Background | Contrast Ratio | WCAG AA |
|------------|------------|----------------|---------|
| --text-primary (#F5F0E7) | --surface (#16161A) | 13.5:1 | ✅ AAA |
| --text-muted (#8A8882) | --surface (#16161A) | 5.2:1 | ✅ AA |
| --brass (#D4A843) | --surface (#16161A) | 5.8:1 | ✅ AA |
| --danger (#C8553D) | --surface (#16161A) | 4.2:1 | ✅ AA (large text) |

## Keyboard Navigation
| Shortcut | Action |
|----------|--------|
| 1-4 | Switch sections |
| Escape | Close drawer / cancel drag |
| Tab | Cycle focus through rail items |
| Enter/Space | Activate button, confirm patch |
| Arrow keys (on knob) | Adjust parameter |

## ERD References
- No accessibility-specific database tables

## Rules
1. All interactive elements must be keyboard accessible
2. All images must have alt text
3. All form inputs must have associated labels
4. Color must not be the only differentiator (use icons + text)
5. Touch targets minimum 44×44px (48×48px preferred)
6. Focus indicators must be visible (2px solid --brass outline)
7. ARIA roles must match semantic HTML elements

## Examples
- Login form: `<label htmlFor="email">{t('auth.email')}</label>` + `<input id="email" aria-required="true">`
- Knob: `<button class="knob" role="tab" aria-selected="false" aria-label="Library section" tabindex="0">`
- Cable: 20px transparent hit area for pointer events

## Edge Cases
- Screen reader handling of synth metaphor terminology ("knob", "cable", "jack")
- RTL screen readers (Arabic JAWS/NVDA behavior)
- Custom components with non-standard ARIA roles
- Colorblind users distinguishing teal/brass/success/danger

## Failure Cases
- Missing aria-label on icon-only buttons
- Insufficient color contrast on text-muted (#8A8882) for small text
- Keyboard trap in user drawer when open
- Touch target smaller than 44×44px

## Recovery Procedures
1. Run Lighthouse accessibility audit
2. Verify keyboard navigation through all interactive elements
3. Check ARIA labels with screen reader
4. Fix color contrast issues in design tokens

## Refactoring Strategy
- Add automated a11y checks to CI (axe-core)
- Create accessibility testing checklist
- Document screen reader behavior for all components
- Plan for WCAG AAA compliance
