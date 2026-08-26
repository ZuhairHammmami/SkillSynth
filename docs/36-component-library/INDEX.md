# SS-EDS: Component Library

## Purpose
Document the shared component library: 21 shadcn/ui primitives re-exported from `shared/ui/`, plus custom application components in `shared/components/`. All components follow the Linear/Notion design tokens and accept standard Tailwind className overrides.

## Responsibilities
- Maintain shadcn/ui primitives (Button, Input, Card, Dialog, etc.) with consistent styling
- Provide custom application components (Logo, LocaleSwitcher, Loading)
- Ensure all components support RTL via logical CSS properties
- Export all components from barrel index files for clean imports

## Inputs
- UI design system tokens (20-ui-system)
- Radix UI primitives (shadcn/ui foundation)
- Tailwind CSS configuration (colors, animations, border-radius)

## Outputs
- 21 shadcn/ui component files in `shared/ui/`
- Custom components in `shared/components/`
- Barrel exports from `shared/ui/index.ts` and `shared/components/index.ts`
- Consistent import pattern: `@/shared/ui/button`

## Dependencies
- 20-ui-system (design tokens, color map)
- 08-frontend (component usage across all pages)
- 21-accessibility (Radix UI built-in ARIA)

## Component Index — `shared/ui/` (shadcn/ui Primitives)
| Component | File | Radix Dependency | Purpose |
|-----------|------|-----------------|---------|
| Accordion | accordion.tsx | @radix-ui/react-accordion | Collapsible sections |
| Alert | alert.tsx | — | Inline notification messages |
| AlertDialog | alert-dialog.tsx | @radix-ui/react-alert-dialog | Destructive confirmations |
| Avatar | avatar.tsx | @radix-ui/react-avatar | User profile images |
| Badge | badge.tsx | — | Status/ category labels |
| Button | button.tsx | @radix-ui/react-slot | All clickable actions (variant, size, asChild) |
| Card | card.tsx | — | Content containers |
| Dialog | dialog.tsx | @radix-ui/react-dialog | Modal overlays |
| DropdownMenu | dropdown-menu.tsx | @radix-ui/react-dropdown-menu | Context menus |
| Form | form.tsx | react-hook-form + zod | Form with validation |
| Input | input.tsx | — | Text inputs |
| Label | label.tsx | @radix-ui/react-label | Form labels |
| Progress | progress.tsx | @radix-ui/react-progress | Progress bars |
| RadioGroup | radio-group.tsx | @radix-ui/react-radio-group | Radio button groups |
| Select | select.tsx | @radix-ui/react-select | Dropdown selects |
| Sheet | sheet.tsx | — | Slide-over panels |
| Skeleton | skeleton.tsx | — | Loading placeholders |
| Slider | slider.tsx | @radix-ui/react-slider | Range inputs |
| Sonner | sonner.tsx | sonner | Toast notifications |
| Table | table.tsx | @tanstack/react-table | Data tables |
| Tabs | tabs.tsx | @radix-ui/react-tabs | Tabbed interfaces |

## Custom Components — `shared/components/`
| Component | File | Purpose |
|-----------|------|---------|
| Logo | Logo.tsx | Application logo with link |
| LocaleSwitcher | LocaleSwitcher.tsx | Language toggle (shows opposite language name) |
| Loading | Loading.tsx | Full-page spinner |

## Composition Patterns
- All components accept `className` prop merged via `cn()` utility (clsx + tailwind-merge)
- Variants via class-variance-authority (`cva()`) — see Button, Badge
- `asChild` pattern via `Slot` from Radix for polymorphic components
- Form components use `react-hook-form` + `zod` resolver for validation

## Typical Import Pattern
```typescript
import { Button } from '@/shared/ui/button';
import { Card, CardHeader, CardContent } from '@/shared/ui/card';
import { useTranslations } from 'next-intl';
import { cn } from '@/shared/lib/utils';
```

## Sequence: Component Usage
```
Page → import { Button } from '@/shared/ui/button' → <Button variant="primary" size="sm"> → cn() merges classes → renders <button> with Tailwind + CVA classes
```

## Rules
1. All components use CSS variables from `:root` — no hardcoded color values
2. Every component must accept and merge `className` via `cn()`
3. shadcn/ui components must not be customized beyond theme CSS variables
4. Naming: kebab-case filename, PascalCase export
5. Internal state (open/closed for dialog) managed by consumer, not component
6. Barrel exports in `shared/ui/index.ts` re-export all primitives

## Examples
- Button variants: `default` (primary blue), `secondary` (muted), `ghost` (transparent), `destructive` (red), `outline` (bordered)
- Card: `<Card><CardHeader><CardTitle/><CardDescription/></CardHeader><CardContent/></Card>`
- Badge: `<Badge variant="default|secondary|destructive|outline">`

## Edge Cases
- Component receives invalid variant → TypeScript compile error
- Long text in Button → truncation with `truncate` utility class
- Dialog portal: renders at document root for proper stacking

## Failure Cases
- Import from wrong path → module resolution failure
- Missing Radix peer dependency → runtime error
- cn() class conflict → last class wins (undesired override)

## Recovery Procedures
1. Verify export in `shared/ui/index.ts`
2. Check shadcn/ui `components.json` configuration
3. Ensure Radix version matches package.json

## Refactoring Strategy
- Add Storybook for visual documentation
- Extract to external npm package for cross-project reuse
- Add unit tests with React Testing Library for each component
