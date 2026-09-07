# SkillSynth Thesis — Warm Craft Formatting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reformat `brand/cover/thesis/الأطروحة.docx` (an Arabic thesis, 7 chapters, 56 pp) according to the SkillSynth "Warm Craft" identity with no wording changes.

**Architecture:** Edit the OOXML directly (unzip → edit document.xml / styles.xml / header+footer XMLs → rezip → validate) using the docx skill workflow and the `docx.py` XSD validator. A single lxml-driven Python script performs run splitting + border-boxing of English terms and numbers, heading/caption/body restyling, and table styling. Header/footer and TOC are added as Word fields (STYLEREF / PAGE / TOC).

**Tech Stack:** Python (lxml, defusedxml), OOXML/DOCX, LibreOffice (soffice → PDF) + Poppler (pdftoppm/pdftotext) for verification, the repo's `docx.py` validator.

**Spec:** Approved plan — Warm Craft identity from `brand/identity/{guidelines,palette,typography}`; no text additions/deletions/rewordings; equation boxes = inline thin-bordered runs around every English term and number; header = STYLEREF section title + hairline; footer = PAGE field; live field TOC.

## Global Constraints

- **No text additions/deletions/rewordings.** Run-splitting changes only formatting boundaries (rendered text identical). Verify via concatenated-text diff against baseline.
- Colors ONLY from Warm Craft canonical palette (`brand/identity/palette.json`): paper `#FBF6EC`, paper-2 `#F3EDE1`, card `#FFFDF7`, ink `#2A2521`, ink-soft `#4A4238`, clay `#8A7B6C`, ochre `#B5862E`, ochre-deep `#8A6520`, sage `#7C8A6B`, sage-deep `#5F6C50`, line `#E4DAC8`, line-strong `#CFC3AE`. Banned: gradients, neon, glassmorphism.
- Fonts by role (`typography.md`): Arabic body Noto Sans Arabic; Arabic display El Messiri; Latin body Public Sans; Latin display Bricolage Grotesque. Arabic: no italics. Declared family strings authoritative (fallback at render OK).
- Equation box = single hairline border, color `line-strong #CFC3AE`, sz ≈ 6–8 (≈1px), tight padding; punctuation stays unboxed.
- RTL-first; Arabic body justified with RTL alignment.
- Must pass `docx.py` validator (XSD, whitespace, deletions=0) with `--original` for paragraph-count diff, and every `<w:del>` added count = 0.

---

## Task 1 — Working copy & safety baseline

- Create `brand/cover/thesis/work/` via docx-skill workflow: copy `الأطروحة.docx` → `thesis-work.docx`; unzip to `work/unpacked/`; delete symlink entries.
- Snapshot baseline: concatenate all `w:t` → `work/baseline.txt` + sha256 stored for Task 8 compare.
- Do NOT run `merge_runs.py` (it can merge Arabic+English runs the boxer must split).

## Task 2 — Styles.xml → Warm Craft

- `docDefaults`: fonts Noto Sans Arabic + Public Sans; sz 22 (11pt); color ink `#2A2521`.
- Recolor heading styles 831–836, 850 (Title), 869 (Caption) from navy `0f4761`/`0e2841` → ink / ink-soft / ochre-deep accents.
- Ensure outlineLvl on heading styles; set body/heading bidi font.
- Header/Footer style fonts to body; hyperlink → ochre-deep.

## Task 3 — Core format script

`brand/cover/thesis/scripts/format_thesis.py` operating in place on `work/unpacked/word/document.xml`:
1. Heading sweep (831–834): pageBreakBefore for 831; spacing; ochre-deep bottom hairline for 831/832; inline navy→ink.
2. Box pass: split mixed Arabic+digit runs; box every Latin segment and every digit segment (w:bdr); strip boundary punctuation out of the box; leave pure-Arabic runs; assert concatenated text unchanged per paragraph.
3. Captions `الشكل (N-M):` / `الجدول (N-M):`: caption style, centered, ink-soft; box the parenthesized number + "الشكل/الجدول" label handling.
4. Body: RTL justify, first-line indent, Arabic line spacing (~1.75), spacing after, bidi font.

## Task 4 — Tables → Warm Craft

Hairline borders (line/line-strong), header row shading paper-2 + bold ink, box English cell values, sensible column widths.

## Task 5 — Section layout

Book margins (mirror/gutter), A4 portrait, keep titlePg, one section.

## Task 6 — Header & Footer

Footer: PAGE field centered, ink-soft, top hairline; header: STYLEREF section title, ink-soft, bottom hairline; first-page blank. Wire headerReference/footerReference with r:id + content-type overrides.

## Task 7 — TOC → live field

Replace static TOC paragraphs with a `TOC \o "1-3" \h \z \u` field; TOC Heading style Warm Craft.

## Task 8 — Verification

docx.py validator (--original); concatenated-text diff vs baseline (0 changes except intended TOC region); render PDF via soffice; pdftotext checks (pages non-empty, headings, page numbers, tables intact, no clipping); field-update pass so TOC/STYLEREF/PAGE resolve; produce `الأطروحة-formatted.docx`, leave original untouched.
