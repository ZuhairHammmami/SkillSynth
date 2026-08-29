# Typography — Warm Craft

This file is part of the canonical SkillSynth brand identity. It pairs with the
color system in `palette.json` and the usage rules in `guidelines.md`. SkillSynth
is a bilingual learning OS — Arabic-first RTL, English LTR — so type must serve
both directions without compromise.

---

## Fixed Type System

Four families carry the brand. Latin display is the visual primary; Arabic joins
it only as accent words and RTL-first body.

| Role | Latin font | Arabic font |
|------|-----------|-------------|
| Display | Bricolage Grotesque (optical 12..96) | El Messiri |
| Body / UI | Public Sans | Noto Sans Arabic |

Modular scale is 1.067 (minor second). The ladder, in px, ascending from 10:

```
10.00 10.67 11.40 12.16 12.98 13.85 14.78 15.77 16.83
17.97 19.18 20.47 21.84 23.31 24.87 26.54 28.32 30.23
32.26 34.43 36.75 39.22 41.86 44.67
```

---

## 1. Roles

| Role | Size (px) | Size (rem) | Weight | Line-height | Letter-spacing | Fonts |
|------|-----------|------------|--------|-------------|----------------|-------|
| Display | 44.67 | 2.79 | Bricolage Grotesque 800 · El Messiri 700 | 1.05 | -0.02em Latin / 0 Arabic | Bricolage Grotesque, El Messiri |
| Heading | 28.32 | 1.77 | 700 | 1.15 | -0.01em Latin / 0 Arabic | Bricolage Grotesque, El Messiri |
| Subheading | 19.18 | 1.20 | 600 | 1.25 | 0 | Public Sans, Noto Sans Arabic |
| Body | 16.83 (~16px) | 1.05 | 400 | 1.6 Latin / 1.75 Arabic | 0 | Public Sans, Noto Sans Arabic |
| Caption | 13.85 (~14px) | 0.87 | 400 | 1.5 | 0 | Public Sans, Noto Sans Arabic |
| Footnote | 11.40 (~11px) | 0.71 | 400 | 1.4 | 0 | Public Sans, Noto Sans Arabic |

Reserved use:

- **Display** — cover titles and hero moments only. Never paragraph text.
- **Heading** — section titles and card headers.
- **Subheading** — secondary titles and emphasized labels.
- **Body** — the product's working size. Default for nearly all content.
- **Caption** — metadata, timestamps, and supporting labels.
- **Footnote** — legal, sourcing, and fine print.

---

## 2. Script Pairing Rules

- **English is the display primary** (product decision). Cover titles, hero
  headlines, and brand moments are English by default.
- **Arabic is used for accent words** and RTL-first body copy. A single Arabic
  display word may elevate a title — e.g. مسارك ("your path").
- **El Messiri is used ONLY for Arabic display words.** Never for running Arabic
  text; never for paragraphs or UI labels.
- **Arabic body is always Noto Sans Arabic.**
- **Latin body is always Public Sans.**
- **NEVER substitute Bricolage Grotesque for Arabic** — it has no Arabic glyphs
  and must never be asked to render one.
- **NEVER let El Messiri render Latin.** If an Arabic display token is removed,
  the surrounding Latin headline returns to Bricolage Grotesque.

---

## 3. RTL Mirroring

The mirrored scale is identical; the differences are **metrics, not sizes.**

- **Arabic line-height +0.15** — body rises from 1.6 to 1.75 so diacritics and
  tall ascenders breathe.
- **Letter-spacing 0** — no negative tracking in Arabic. Arabic has no tracking
  convention; digits and joins collapse if letterspace is squeezed.
- **No italics** — Arabic has no italic form. Never fake one with slant or skew.
- **No forced justification** — use `text-align: start` under `direction`.
  Arabic justification with script shaping is fragile and beyond scope.
- **Longer x-height tolerance** — Arabic body may run one size down when mixed
  in Latin UI containers. A 14px Arabic string inside a 16px cell keeps optical
  balance without crowding the row.

---

## 4. Font Loading

Load all four faces in one request via Google Fonts CSS2 `@import`:

```css
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=El+Messiri:wght@400..700&family=Noto+Sans+Arabic:wght@100..900&family=Public+Sans:ital,wght@0,100..900;1,100..900&display=swap');
```

Declare the token block on `:root`:

```css
:root {
  --font-display: 'Bricolage Grotesque', 'El Messiri',
    ui-sans-serif, system-ui, sans-serif;
  --font-body: 'Public Sans', 'Noto Sans Arabic',
    ui-sans-serif, system-ui, sans-serif;
  --font-ar: 'Noto Sans Arabic', 'El Messiri',
    ui-sans-serif, system-ui, sans-serif;
}
```

Apply Arabic by language tag. Under `:lang(ar)` set `font-family: var(--font-ar)`.
Arabic **display** words — the مسارك-type accents — get `font-family: 'El Messiri'`
explicitly, overriding the body stack.

---

## 5. Usage Notes

- **Pair display + body only.** Never set three families in one view.
- **Max two sizes per view**, except tables where size is a data-density
  necessity.
- **No ALL CAPS in Arabic.** Arabic capitals do not exist; forcing letterforms
  is wrong. Arabic reads case-free always.
- **English titles keep Sentence case** — not ALL CAPS, not Title Case.
- **Hyphenation off.** Ragged, unbroken line endings on both scripts.
- **Tabular figures** via `font-feature-settings: 'tnum'` for numbers in
  assessments and scores only — anywhere digit alignment matters. Nowhere else.

---

## 6. Local-Fallback Caveat

Brand SVG and PDF previews in this repository render Bricolage Grotesque,
El Messiri, and Public Sans via fontconfig fallbacks — typically Noto Sans and
Noto Sans Arabic — because the licensed faces are not installed in this
environment.

Those fallbacks are preview-only. The **declared `font-family` strings in every
SVG are authoritative.** Do not "fix" the fallback appearance; trust the
declared stack and verify against a machine that has the real fonts installed.

---

*Sibling files: `palette.json` (color), `guidelines.md` (usage).*