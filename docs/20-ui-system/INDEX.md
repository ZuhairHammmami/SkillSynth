# SS-EDS: UI System

## Purpose
Document the visual design system: Linear/Notion/Stripe-inspired aesthetics with HSL-based tokens, whitespace-first layout, consistent spacing, and professional typography.

## Responsibilities
- Maintain CSS custom properties (HSL design tokens) in `globals.css`
- Enforce whitespace-first approach: generous padding, consistent 8px grid
- Define typography system (Tajawal via next/font)
- Maintain component styling guidelines for shadcn/ui primitives
- Ensure visual consistency across all 24 routes

## Inputs
- shadcn/ui default theme as foundation
- Accessibility contrast requirements (WCAG 2.1 AA)
- RTL typography research (Tajawal font characteristics)

## Outputs
- HSL design tokens in `:root` CSS
- Tailwind CSS configuration (colors, animations, border-radius)
- Component styling conventions
- Spacing and layout guidelines

## Dependencies
- 00-principles (flat design, no gradients, RTL-first)
- 36-component-library (implementation)
- 21-accessibility (color contrast, focus rings)

## Design Tokens (HSL)
| Token | Value | Purpose |
|-------|-------|---------|
| `--background` | 0 0% 100% | Page background |
| `--foreground` | 240 10% 3.9% | Primary text |
| `--card` | 0 0% 100% | Card surface |
| `--primary` | 221 83% 53% | Professional blue — buttons, links |
| `--secondary` | 210 40% 96.1% | Subtle backgrounds |
| `--muted` | 210 40% 96.1% | Muted backgrounds |
| `--muted-foreground` | 215.4 16.3% 46.9% | Secondary text |
| `--destructive` | 0 84.2% 60.2% | Error/destructive actions |
| `--border` | 214.3 31.8% 91.4% | Borders, dividers |
| `--ring` | 221 83% 53% | Focus rings |
| `--radius` | 0.5rem | Default border-radius |

## Spacing System
- Baseline: 8px grid (space-y-1, p-3, gap-4, etc.)
- Page padding: `p-6 lg:p-8` on main content areas
- Card padding: `p-4` to `p-6`
- Sidebar width: `--sidebar-width: 240px` (w-60)
- Max content width: 1400px (container in tailwind config)

## Typography
| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Body | Tajawal / system-ui | 300/400/500 | All body text |
| Headings | Tajawal | 700/800 | Page/ section titles |
| UI labels | Tajawal | 500 | Button, nav, form labels |
| Monospace | system monospace | 400 | Code blocks, data |

Tajawal loaded via Google Fonts with preconnect + preload + print-as-fallback strategy. System UI font stack as fallback.

## Layout Patterns
```
Landing:   Hero → Feature Grid → How It Works → CTA     (server component)
Auth:      Centered form (left) + Marketing panel (right, hidden mobile)
Student:   Fixed sidebar (w-60) + Sticky header + Main content area
Admin:     Fixed sidebar (w-60) + "Admin" badge + Sticky header + Main content
```

## Sequence: Theme Application
```
globals.css :root HSL variables → tailwind.config.js color map → Tailwind classes (bg-background, text-foreground) → Rendered DOM
```

## State Diagram: Visual States
```
[Default] → [Hover] (bg-accent, slight lift) → [Active] (primary bg)
    ↓
[Disabled] (opacity-50, cursor-not-allowed)
    ↓
[Focus] (ring-2 ring-ring)
```

## Rules
1. No gradients, neon, glassmorphism, or heavy shadows — flat solid colors only
2. Border-radius: `--radius` (0.5rem) for components, 2px for cards
3. All spacing follows 8px baseline grid
4. No inline styles — always use CSS variables or Tailwind classes
5. Interactive elements must have visible focus rings (`ring-ring`)
6. Animations: fade-in (0.3s), slide-up (0.3s), scale-in (0.2s) — subtle only

## Examples
- Button: `bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2`
- Card: `rounded-lg border bg-card text-card-foreground shadow-sm p-6`
- Input: `flex h-10 w-full rounded-md border border-input bg-background px-3 py-2`

## Edge Cases
- Dark mode future: all tokens have HSL values that can be inverted via `next-themes`
- RTL: use logical CSS properties (`ms-`/`me-`, `ps-`/`pe-`, `border-s-`/`border-e-`)
- Long text truncation on sidebar nav items

## Failure Cases
- CSS variable not defined in `:root` → fallback to browser default
- Missing Tailwind class → component looks unstyled
- Font not loaded → system UI fallback (acceptable degradation)

## Recovery Procedures
1. Verify `:root` HSL variables in `globals.css`
2. Check tailwind.config.js for color mappings
3. Run `pnpm build` to catch CSS compilation errors

## Refactoring Strategy
- Add dark mode support via CSS variables swap
- Extract design tokens to a separate CSS package
- Add visual regression tests with Chromatic
