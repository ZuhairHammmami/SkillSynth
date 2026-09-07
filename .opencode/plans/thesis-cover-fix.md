# Thesis Cover — Fix & High-Resolution Print Output

**Scope:** `brand/cover/thesis/` — fix design/layout errors in `cover_spec.py` + `build_covers.py`,
correct the Arabic binding side, add the blank inside (verso) sheet, and produce 300 dpi PNGs + a
print PDF with the real typefaces embedded.

---

## Research findings (already verified)

### 1. Binding side is wrong (Arabic / spine-right requested)
- Current jacket lays panels as `back | spine | front`, with FRONT placed at the rightmost sheet
  position (`thesis-jacket.svg`: `front-*` at `translate(646.80 …)`, spine at `604.28`, back at `9`).
- Physical result: in the closed book the **spine lands on the LEFT edge of the front cover**
  (English/LTR-style). The user wants the proper Arabic thesis binding: **spine on the RIGHT** of
  the front cover (front faces you, spine down the right edge, open by lifting the left fore-edge).
- **Fix:** reorder the wrap to **`front | spine | back`** (front leftmost in the flat sheet, spine
  immediately right of front so it bonds to the front cover's right edge, back rightmost).
- The existing docs/comments (`LAYERS.md`, `PRINT_SPEC.md`, `cover_spec.py` `RTL BOOK` note, several
  `build_covers.py` comments) claim "spine-RIGHT / Arabic" but the geometry produced spine-LEFT.
  Update all of them so they accurately describe `front | spine | back` → spine-RIGHT.

### 2. Text / layout overlap (the reported "text/layout overlaps")
Measured with the real **El Messiri** font (now installed): the widest author name
`علي عثمان عبد الملك` ≈ **156 pt wide at the current 14.78 pt size**. In the author 2×2 grid
(columns `CX±86 = 211.64 / 383.64`) it lands only **~1.5 pt** from the identity card's inner edge
(`131.64`) — a visible collision / near-touch.
- **Fix:** reduce author/supervisor name size to **`NAME_SIZE = 13.0`** and rebalance columns:
  - `AUTH_COLS = (CX - 90, CX + 90)` → widest name (~142 pt @13) clears the inner CARD edge by ≈7–9 pt.
  - `SUP_COLS = (CX - 95, CX + 95)` → widest supervisor (~120 pt @13) clears by ≈10–11 pt.
- Other measured text is compliant with the 27 pt safe box (title, description, letterhead,
  abstract lines ≤ ~379 pt wide, year) — no changes needed there, but re-verify after edits.

### 3. Fonts were not installed (rendering was wrong)
- `El Messiri`, `Bricolage Grotesque`, `Public Sans` were **not** installed → every existing
  PNG/PDF rendered with Noto-Sans fallback and mis-measured layout.
- **Done already:** installed the three variable TTFs into `~/.local/share/fonts/`; fontconfig now
  resolves them (verified via `fc-match`). This makes 300 dpi renders and PDF embedding faithful.

### 4. Preview assets are stale
- `preview-front/back/spine/jacket.png` (01:44) predate the SVG/spec code (03:34) and were rendered
  with fallback fonts. Must be re-rendered at 300 dpi after fixes.

---

## Changes to make

### A. `cover_spec.py`
1. Add constant
   ```python
   NAME_SIZE = 13.0   # author/supervisor name size — keeps the widest name off the card edges
   ```
2. Change author grid columns → `AUTH_COLS = (CX - 90.0, CX + 90.0)` (keeps `AUTH_ROWS`, `AUTH_LBL_Y`, `TICK_Y`, `RULE_Y` as-is).
3. Change supervisor columns → `SUP_COLS = (CX - 95.0, CX + 95.0)`.
4. Update the `RTL BOOK` parameter note to: "Jacket order **front | spine | back** ⇒ spine bonds to
   the RIGHT edge of the front cover (Arabic book); open by lifting the LEFT fore-edge."

### B. `build_covers.py`
1. **`front_names()`**: replace the two hard-coded `14.78` with `NAME_SIZE` (authors + supervisors).
2. **`jacket()`** — reorder panels to `front | spine | back`:
   - `fold_front_spine = BLEED + W` (604.28), `fold_spine_back = fold_front_spine + SB` (646.80).
   - Place: `front-bleed-art` + `front-core-art` at `translate(BLEED, BLEED)`; `spine-art` at
     `translate(fold_front_spine, BLEED)`; `back-art` at `translate(fold_spine_back, BLEED)`.
   - Update the `print-guides` layer: crop marks at the 8 boundary points (recompute the two score
     lines to `fold_front_spine` / `fold_spine_back`), section labels → `FRONT` / `SPINE` / `BACK`
     in the new left-to-right reading, and score-line labels in `_crop_mark` (the right-edge/top
     edge tests still hold; verify the media-width guard `x == BLEED + W + SB + W + BLEED`).
   - Update the `note` header via-docstring to describe `front | spine | back`, spine-right.
3. **Add a blank inside/verso sheet** — new `thesis-inside.svg` (same media size as the jacket:
   `WC×HC`, panels `inside-front | inside-spine | inside-back`), each panel just a plain paper rect
   (front-inside = `PAPER`, back-inside & spine-inside = `PAPER2`) so the cover can print on both
   faces. Emit it from `main()` (write `thesis-inside.svg`).
4. **(Recommend)** add a small `render.py` (in the same folder) that calls `rsvg-convert -d 300`
   to produce PNGs and a vector PDF (see E). Keep each function ≤ 40 lines with a purpose docstring
   (project convention).

### C. `print_spec.py` (optional but good)
- Update section labels/order and the `fold_*` names to `front | spine | back`; update its
  section-emitter to render `FRONT | SPINE | BACK` left-to-right. Rename `fold_back_spine`→
  `fold_front_spine`, `fold_spine_front`→`fold_spine_back`.

### D. Docs
- `LAYERS.md` and `PRINT_SPEC.md`: update the "1-up jacket / back|spine|front" narrative to
  `front | spine | back` and the spine-side wording (spine bonds to the RIGHT edge of front).
  Update the mermaid/media cross-section and boundary table accordingly.

### E. Outputs (300 dpi, real fonts)
- After installing fonts (done) and regenerating SVGs, render with `rsvg-convert --dpi-x 300 --dpi-y 300`:
  - `preview-front.png` ≈ 2480×3508 (A4 @300)
  - `preview-back.png` ≈ 2480×3508
  - `preview-spine.png` ≈ 178×3508
  - `preview-jacket.png` ≈ 5216×3583 (media 441.68×303.41 mm @300)
  - `preview-inside.png` ≈ 5216×3583
  - `thesis-jacket.pdf` — vector print PDF via `rsvg-convert --format=pdf` (or LibreOffice).
- Note: all exports stay RGB; convert to CMYK at the print shop (per existing spec).
- Rebuild `LAYERS.md` via `layers_md()`.

---

## Verification (after implementation)

1. **No text collisions / safe margins:** a script using `fontTools` (real El Messiri) measures every
   text element and asserts none overlaps another text box nor crosses the 27 pt safe box or the
   identity-card inner edges. At minimum, programmatically confirm the widest author name now clears
   the card inner edge by ≥ 6 pt.
2. **Spine-side invariant:** assert the front artwork is placed immediately LEFT of the spine panel
   in the jacket (spine at front's right edge, no mirroring of the front artwork).
3. **Renders:** regenerate all SVGs (`python3 build_covers.py`), confirm `thesis-front/back/spine/
   jacket/inside.svg` + `LAYERS.md` are produced; run the 300 dpi rasterizer; confirm PNG resolutions
   and that the PDF opens.
4. **Font check:** `fc-match "El Messiri"` etc. resolve to the installed TTFs (already true).

---

## Notes / decisions locked with the user
- Binding side: **spine on the RIGHT** of the front cover (Arabic). Flat jacket shows
  `front | spine | back`.
- "True two-sided cover": add a **blank inside (verso)** sheet; inside panels stay plain paper.
- Outputs wanted: fixed SVGs + print **PDF** + **300 dpi PNGs**.
- Fonts installed system-wide (user-level) for faithful rendering.
