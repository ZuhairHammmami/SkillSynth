# SkillSynth — "Warm Craft" Brand Identity Guidelines

This file is the canonical usage reference for the Warm Craft identity. It pairs
with `palette.json` (color) and `typography.md` (type). Hex values, geometry, and
contrast ratios quoted here are authoritative.

---

## 1. Brand Statement

SkillSynth is a warm craft above all: an adaptive learning OS that meets every
learner where they are and builds a path from what you already know. Hand-drawn
strokes, paper-toned surfaces, and deliberate restraint replace the
neon-and-gradient posture of typical learning software. The mark — a sprout
rising from a closed path ring — is the whole promise in one glyph: a route out
of what you know and toward what you can become. Nothing in Warm Craft reads as
machine-cold; everything is meant to feel held, guided, and handmade.

---

## 2. The Mark

A hand-drawn sprout rises from a closed rounded "path/book" ring. Every stroke
is 1.8 units with round caps and joins. Master geometry lives in
`brand/identity/logo/construction-grid.svg`.

### Anatomy

| Part | Geometry | Color |
|------|----------|-------|
| Ring (path/book) | ellipse-like closed path | stroke ochre `#B5862E` |
| Stem | line 16,27 → 16,13 | stroke sage-deep `#5F6C50` |
| Leaves | two strokes 16,18 → 11,12 and 16,18 → 21,12 | stroke sage-deep `#5F6C50` |
| Seed | dot at cy=9, r=2.2 | fill ochre `#B5862E` |

### Construction

The glyph is drawn on a 32-unit grid: a 4-unit minor grid, an 8-unit major
grid, and a vertical axis at x=16 that governs the ring, stem, leaves, and seed.
All paths snap to this geometry; do not redraw freehand.

### Approved Color Variants

| Variant | Definition | Where used |
|---------|-----------|------------|
| Main | ochre ring + sage-deep sprout + ochre seed dot | Light grounds: paper / paper-2 / card |
| Monochrome | mark in one color: ink `#2A2521` or paper `#FBF6EC` | One-color print / emboss |
| Inverted | light strokes on dark ground | Dark grounds: ochre-deep `#8A6520` or ink `#2A2521` |

Choose by ground, not by mood: light background → main; single-color
print/emboss → monochrome; dark ochre-deep or ink grounds → inverted.

---

## 3. Clear Space

Minimum clear space around the mark is 25% of the mark's height on all sides —
approximately 8 units of the 32-grid. The wordmark lockup (mark + "SkillSynth")
is treated as one unit: clear space is measured from the lockup's bounding box,
never between the mark and the wordmark.

---

## 4. Minimum Sizes

| Context | Minimum |
|---------|---------|
| Favicon | 16px — mark only |
| Menu / app bar | 24px — mark only |
| Wordmark lockup | 20px total height — absolute minimum |

Never shrink below legibility. Keep the aspect ratio locked — the mark is 1:1
and must never be stretched or squashed. When a space cannot host the lockup at
20px, use the mark alone instead of distorting either.

---

## 5. Do and Don't

| Do | Don't |
|----|-------|
| Keep all strokes at 1.8 with round caps/joins | Recolor the mark in arbitrary hues |
| Put the mark on paper / paper-2 / card tones | Place it on photographic or busy backgrounds |
| Use flat colors from `palette.json` only | Use gradients on or around the mark |
| Keep the mark exactly as the grid draws it, 0° | Rotate beyond the construction grid's 0° |
| Use only the three approved variants | Outline, redraw, or stroke-the-stroke the glyph |
| Set "SkillSynth" in Bricolage Grotesque | Set it in any other typeface |
| Keep "Synth" ochre-deep (color) | Split "Synth" other than ochre-deep (except monochrome) |
| Preserve the 1:1 aspect ratio | Stretch, squash, or shear the mark |
| Keep the seed dot filled ochre in the main variant | Hollow, move, or resize the seed dot |
| Keep hairlines at 1px | Thicken hairlines into status lines |
| Track the wordmark to -0.02em at the tightest | Letter-space the wordmark below -0.02em |
| Add depth with soft, low-opacity shadows | Add drop shadows to the mark |
| Respect 25% clear space on all sides | Crowd the mark against type, icons, or edges |

---

## 6. Typography Usage

- Display faces (Bricolage Grotesque Latin, El Messiri Arabic) are reserved for
  titles and hero moments only — never paragraph text.
- At most one Arabic display accent word per view (e.g. مسارك). All other
  Arabic is Noto Sans Arabic; all other Latin is Public Sans.
- Pair one display face with one body face. Never set three families in a view,
  and cap content at a light 1.067-scale ladder run.

Size and contrast rules apply exactly:

| Text | Minimum contrast |
|------|------------------|
| Small body text | 4.5:1 (WCAG AA) |
| Display / large text | 3:1 (WCAG AA large) |

Ochre `#B5862E` (3.04:1 on paper) and sage `#7C8A6B` (3.42:1 on paper) are
display-only on paper — never small body text. For legible text use ochre-deep
`#8A6520` (4.92:1) and sage-deep `#5F6C50` (5.20:1). Ink on paper is 14.08:1;
ink-soft on paper is 9.16:1.

---

## 7. Color Application

| Role | Token | Behavior |
|------|-------|----------|
| Surface base | paper `#FBF6EC` | Page and canvas background |
| Surface inset | paper-2 `#F3EDE1` | Back covers, panels, soft dividers |
| Surface elevated | card `#FFFDF7` | Cards and inputs lifted off paper |
| Emphasis | ochre `#B5862E` | Large display accents, ring, seed — used rarely |
| Links / CTAs / accent text | ochre-deep `#8A6520` | AA text; wordmark "Synth"; marker underlines |
| Fields / illustration | sage `#7C8A6B` | Serene fields, leaf-stage mid tone, bands |
| Sprout / deep accent | sage-deep `#5F6C50` | Stem and leaves; deep sage type (AA) |
| Status | success `#5C7A5E` · warning `#B45309` · danger `#A23B2E` | Warm set; see palette.json |
| Hairlines | line `#E4DAC8` · line-strong `#CFC3AE` | Decorative only — never text |
| Focus ring | ochre-deep `#8A6520` (`ring`) | Focus outline and glow (subtle only) |

---

## 8. Voice and Geometry

- **Hairline over shadow.** Depth comes from 1px hairlines first, soft
  low-opacity shadows second — never heavy borders or deep drop shadows.
- **Tiny radii.** Corners stay in the 2–6px band; the mark's own curves lead.
- **Hand-drawn linework.** The 1.8-stroke, round-cap style of the mark is the
  house line style for icons, route dashes, and illustration. Paper grain is
  allowed as an optional texture.
- **Marker underlines.** A hand-drawn marker underline in ochre-deep may
  emphasize a single accent word — never whole paragraphs.
- **Logical, RTL-first layout.** Use logical properties
  (`margin-inline-start`, `padding-inline-end`, `text-align: start`) and
  declare direction from the root; the design mirrors cleanly between
  Arabic RTL and English LTR.
- **Banned.** Gradients, neon, glassmorphism, and drop shadows under light text
  are excluded from every surface, cover, and component.

---

## 9. Print and Production

- Covers print full-bleed with a 0.125in bleed and 0.375in safe margins; keep
  all critical type, the mark, and the spine content inside the safe area.
- `brand/cover/jacket.pdf` is produced from `jacket.svg` via `rsvg-convert` and
  is RGB. Convert it to CMYK at the print shop — do not print the RBG PDF
  directly and do not attempt a lossy conversion in the repo.
- Repository previews of brand SVGs and PDFs render with fallback fonts
  (Noto Sans / Noto Sans Arabic) because Bricolage Grotesque, El Messiri, and
  Public Sans are not installed on this machine. The declared `font-family`
  strings in the SVGs are authoritative; do not "fix" fallback appearance.

---

## 10. Delivery Map

| File | Purpose |
|------|---------|
| `brand/identity/logo/construction-grid.svg` | Master 32-unit construction grid with annotations |
| `brand/identity/logo/main.svg` | Primary lockup: mark + "SkillSynth" wordmark |
| `brand/identity/logo/main.png` | Raster export of the primary lockup |
| `brand/identity/logo/mark-only.svg` | The glyph alone (favicon and small-UI source) |
| `brand/identity/logo/monochrome.svg` | Single-color variant for print and emboss |
| `brand/identity/logo/inverted.svg` | Light-on-dark variant for ochre-deep / ink grounds |
| `brand/identity/logo/favicon.svg` | 16px-safe mark for browser favicons |
| `brand/identity/palette.json` | Canonical color roles, hexes, and WCAG contrast |
| `brand/identity/palette.css` | `:root` tokens plus legacy aliases (app drop-in) |
| `brand/identity/typography.md` | Type system, script pairing, RTL mirroring |
| `brand/identity/guidelines.md` | This file: usage rules and delivery map |
| `brand/cover/jacket.svg` | Cover jacket source (raw SVG) |
| `brand/cover/jacket.pdf` | Jacket preview export (RGB — convert to CMYK at the shop) |
| `brand/cover/views.svg` | Spine + front + back layout preview |
| `brand/cover/display-front.svg` | Front cover flat preview |
| `brand/cover/display-back.svg` | Back cover flat preview |
| `brand/social/og.svg` | Open Graph image source |
| `brand/social/og.png` | Open Graph raster export |

---

## 11. App-Token Migration Note

`brand/identity/palette.css` is a drop-in `:root` replacement mirroring the
`app.css` convention. The legacy aliases already resolve the prior navy / blue
flip, so existing components render Warm Craft without edits:

```css
--bg: var(--paper);
--accent: var(--ochre);
--accent-deep: var(--ochre-deep);
--accent-soft: var(--ochre-soft);
--muted: var(--clay);
```

Favor the new named tokens (`--paper`, `--ochre`, `--sage-deep`, `--line`, and
so on) on all new work; keep the aliases only as a compatibility seam until
legacy components are migrated.