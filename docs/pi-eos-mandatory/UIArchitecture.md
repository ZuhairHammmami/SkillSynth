# UI Architecture

## Design Philosophy
- **Enterprise**: Clean, professional, no neon/gradients/glassmorphism
- **Educational**: Clear hierarchy, readable typography, spacious layouts
- **Trustworthy**: Consistent spacing, predictable interactions
- **Timeless**: Avoid trend-driven design, prioritize long-term maintainability

## Color System (HSL Tokens)
| Token | Value | Usage |
|-------|-------|-------|
| `--background` | 0 0% 100% | Page backgrounds |
| `--foreground` | 240 10% 3.9% | Primary text |
| `--primary` | 221 83% 53% | Primary actions, links |
| `--secondary` | 210 40% 96.1% | Secondary surfaces |
| `--muted` | 210 40% 96.1% | Muted backgrounds |
| `--accent` | 210 40% 96.1% | Accent elements |
| `--destructive` | 0 84.2% 60.2% | Errors, destructive actions |

## Typography
- **Primary Font**: Tajawal (Arabic-first, supports Latin)
- **Fallback**: system-ui, sans-serif
- **Scale**: 12/14/16/18/20/24/30/36px via Tailwind

## Layout System
- **Auth Pages**: Centered form (max-w-md) with right-side illustration
- **Student App**: Sidebar (w-60) + sticky header + main content (p-6 lg:p-8)
- **Admin App**: Same pattern with admin-specific sidebar (11 nav items)
- **Landing**: Full-width hero + feature sections + stats + CTA

## Component Library (shadcn/ui)
21 primitives: Button, Card, Input, Select, Dialog, Avatar, Badge, Table, Slider, RadioGroup, Combobox, Label, Sonner (toast), etc.
