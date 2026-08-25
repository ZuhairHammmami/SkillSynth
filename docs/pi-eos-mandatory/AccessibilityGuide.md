# Accessibility Guide

## Standards
- Target: WCAG AA (minimum), AAA where practical
- Verified via: Manual keyboard navigation, screen reader testing (NVDA)

## Key Requirements
| Requirement | Implementation |
|-------------|---------------|
| Keyboard Navigation | All interactive elements reachable via Tab/Shift+Tab |
| Focus Indicators | Visible focus ring (ring-2 ring-primary) on all interactive elements |
| ARIA Labels | `aria-label` on icon-only buttons, `role` on custom components |
| Semantic HTML | `nav`, `main`, `article`, `aside`, `header`, `footer` as appropriate |
| Color Contrast | Minimum 4.5:1 for normal text, 3:1 for large text |
| Touch Targets | Minimum 44x44px for mobile interactive elements |
| Screen Reader | Alt text on all images, proper heading hierarchy (h1→h2→h3) |

## RTL-Specific
- Direction-aware CSS (start/end instead of left/right)
- Mirror icons for RTL where appropriate
- Text alignment follows document direction
- Form inputs maintain correct visual order in both directions

## Testing
```bash
# Manual checks
- Tab through all pages (no focus traps)
- Verify all form submissions work via keyboard only
- Test with screen reader (NVDA/Orca)
- Verify zoom up to 200% no horizontal scroll
```
