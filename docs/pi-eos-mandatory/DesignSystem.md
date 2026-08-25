# Design System

## Token Structure
All design tokens are defined as HSL CSS variables in `globals.css` and consumed via Tailwind's `hsl(var(--token))` syntax.

## Forbidden Design Elements
- ❌ Neon colors, glow effects
- ❌ Glassmorphism (frosted glass, backdrop blur)
- ❌ Template hero sections with gradients
- ❌ Random/arbitrary gradients
- ❌ Dashboard clutter (dense widgets, gauges, excessive data)
- ❌ Gamification UI (XP bars, level indicators, badges)

## Required Design Elements
- ✔ Clean whitespace (generous padding, max-w constraints)
- ✔ Professional color palette (blue primary, gray neutrals)
- ✔ Educational layout (clear information hierarchy)
- ✔ Trustworthy interactions (predictable, consistent)
- ✔ Responsive (mobile-first, breakpoints at 640/768/1024/1280px)
- ✔ Accessible (WCAG AA contrast, large touch targets)
- ✔ Fast (minimal animation, no layout shifts)

## Component Patterns
| Component | Pattern | States |
|-----------|---------|--------|
| Buttons | Solid (primary), Outline, Ghost, Destructive | default, hover, active, disabled, loading |
| Cards | Rounded border, shadow-sm, p-6 | default, hover (border color change) |
| Inputs | Border, rounded-md, focus ring (primary) | default, focus, error, disabled |
| Tables | Border-collapse, sticky header, hover rows | default, sort, selected |
| Navigation | Sidebar w-60, collapsible on mobile, active indicator | default, active, hover |
