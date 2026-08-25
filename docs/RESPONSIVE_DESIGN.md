# Responsive & Cross-Device Design Specification

## Design Philosophy

The synthesizer metaphor drives all responsive adaptations. On large screens the interface is an infinite modular synth rack. On small screens it becomes a single-column signal chain with a bottom control deck. Every breakpoint preserves the core interactions — patch cables, knobs, jacks, spectrograms — while adapting their spatial layout to the available canvas.

---

## 1. Breakpoint Definitions

| Breakpoint | Range | Canvas Model | Grid Dot Spacing | Primary Navigation | Workspace Mode |
|---|---|---|---|---|---|
| **Desktop XL** | ≥1440px | Infinite canvas, free-form module placement | 40px | Full top command rail | Free-form (X+Y scroll) |
| **Desktop/Laptop** | 1024–1439px | Infinite canvas, free-form module placement | 32px | Full top command rail | Free-form (X+Y scroll) |
| **Tablet** | 768–1023px | Scrollable vertical rack, modules full-width | 24px | Compact top rail | Vertical-only scroll |
| **Phone** | <768px | Single-column card stack | None (no grid visible) | Bottom tool case (top rail hidden) | Vertical-only scroll |

### 1.1 Root CSS Custom Properties by Breakpoint

```css
:root {
  /* Base tokens — every breakpoint inherits these unchanged */
  --bg-root: #0B0B0D;
  --surface: #16161A;
  --brass: #D4A843;
  --teal: #3D5A5C;
  --text-primary: #F5F0E7;
  --text-muted: #8A8882;
  --success: #6A8A5C;
  --danger: #C8553D;

  /* Spacing grid — invariant at 8px */
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 40px;
  --space-6: 48px;
}

@media (min-width: 1440px) {
  :root {
    --grid-dot: 40px;
    --rail-height: 56px;
    --knob-diameter: 40px;
    --module-radius: 2px;
    --font-scale: 1.0;  /* 16px base */
  }
}

@media (min-width: 1024px) and (max-width: 1439px) {
  :root {
    --grid-dot: 32px;
    --rail-height: 56px;
    --knob-diameter: 36px;
    --module-radius: 2px;
    --font-scale: 0.9375;  /* 15px base */
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  :root {
    --grid-dot: 24px;
    --rail-height: 48px;
    --knob-diameter: 32px;
    --module-radius: 2px;
    --font-scale: 0.875;  /* 14px base */
  }
}

@media (max-width: 767px) {
  :root {
    --grid-dot: 0;        /* hidden on phone */
    --rail-height: 0;     /* top rail hidden */
    --tool-case-height: 64px;
    --knob-diameter: 24px;
    --module-radius: 2px;
    --font-scale: 0.875;  /* 14px base */
    --phone-safe-area-bottom: 20px;  /* for notched devices */
  }
}
```

---

## 2. Top Command Rail Adaptation

### 2.1 Desktop (≥1024px)

- **Height**: 56px (`--rail-height`)
- **Background**: `--surface`
- **Bottom border**: 1px solid `--brass`
- **Padding**: 16px horizontal (`--space-2`), 0 vertical
- **Display**: flex, align-items center, justify-content space-between
- **Gap**: 12px between item groups

#### Left cluster (logo + navigation)
- Logo icon: 36px × 36px, no label text
- Navigation items: inline-flex, 14px/1.4 `--text-primary`, uppercase, letter-spacing 0.5px
  - Active nav item: `--brass` underline (2px bottom border, 4px padding below)
  - Hover: `--brass` text color, 100ms ease

#### Center cluster (knobs)
- Array of 4–6 parameter knobs, each:
  - Diameter: 40px, border-radius: 50% (knobs only)
  - Background: `--surface`, border: 1.5px solid `--text-muted`
  - Indicator line: 2px tall, `--brass`, rotates from 7 o'clock position (default)
  - Label: 10px/1.2 `--text-muted`, centered below knob, margin-top 4px
  - Spacing: 16px between knob+label pairs

#### Right cluster (user module)
- Avatar: 36px × 36px, border-radius: 50%
- Wave ring: 44px × 44px circle centered on avatar, border 2px solid `--teal`
  - Wave animation: two concentric rings pulse outward (opacity 0.6 → 0, scale 1 → 1.3, 2s infinite, stagger 1s)
- Username: 14px/1 `--text-primary`, margin-left 8px
- Dropdown caret: 8px × 8px triangle (CSS border), `--text-muted`, margin-left 4px

### 2.2 Tablet (768–1023px)

- **Height**: 48px
- **Background**: `--surface`
- **Bottom border**: 1px solid `--brass`
- **Padding**: 12px horizontal, 0 vertical
- **Gap**: 6px between items

#### Left cluster
- Logo icon: 28px × 28px
- Navigation: text hidden, icons only (24px × 24px each)
  - Active: `--brass` fill, inactive: `--text-muted` fill
  - Tooltip on hover/tap: appears after 400ms, `--surface` bg, 1px `--brass` border, text `--text-primary` 12px

#### Center cluster (knobs)
- Knobs: 32px diameter
- Text labels: REMOVED entirely
- Tooltip on hover/tap (400ms delay): shows knob name, 12px `--text-primary`
- Spacing: 8px between knobs
- Number of knobs displayed: reduce from 6 to 4 (hide 2 rightmost, accessible via overflow menu if needed)

#### Right cluster (user module)
- Avatar: 28px × 28px
- Wave ring: 32px × 32px
  - Simplified: only 2 dots (4px × 4px, `--teal`) orbiting opposite sides of the ring
  - Animation: dots rotate 360° over 3s, linear, infinite
- Username and dropdown: hidden

### 2.3 Phone (<768px)

- **Top rail is completely removed** — no logo, no knobs, no user module at top
- All controls migrate to the **Bottom Tool Case** (see §3)

---

## 3. Bottom Tool Case (Phone)

### 3.1 Structure

- **Position**: fixed to bottom of viewport
- **Height**: 64px (`--tool-case-height`)
- **Width**: 100% of viewport
- **Background**: `--surface`
- **Top border**: 1px solid `--brass`
- **Z-index**: 1000
- **Padding**: 0 12px horizontal
- **Display**: flex, align-items center, justify-content space-around
- **Safe area**: On notched devices, add `padding-bottom: var(--phone-safe-area-bottom, 20px)` and increase height to 84px total (64px + 20px)

### 3.2 Icon Buttons

Five icon buttons, evenly distributed (flex: 1):

| Position | Label | Icon | Default State |
|---|---|---|---|
| 1st | Library | Book/stacked squares (24×24) | Inactive |
| 2nd | Paths | Signal path with arrows (24×24) | Inactive |
| 3rd | Create | Patch jack circle (36×36) | Always active |
| 4th | Tests | Waveform (24×24) | Inactive |
| 5th | User | Avatar silhouette (24×24) | Inactive |

#### Styling
- Icon size: 28px × 28px (except Create which is 36px × 36px)
- Stroke width: 2px, no fill
- Active section: stroke `--brass`
- Inactive: stroke `--text-muted`
- Hover/tap: icon scales to 32px (36px for Create) over 100ms ease
- Tap feedback: brief `--brass` background flash (80ms, opacity 0.15) on the icon's 44px hit area
- Touch target: minimum 48px × 48px invisible hit area centered on each icon

### 3.3 Create Action (Center Button)

- Icon: a patch jack symbol (circle with inner dot, `--brass` stroke 2.5px)
- Size: 36px × 36px
- On tap: opens **Floating Action Menu**

#### Floating Action Menu
- Position: absolute, bottom 72px (64px tool case + 8px gap), centered horizontally
- Width: 140px
- Height: auto (three items, each 40px)
- Background: `--surface`
- Border: 1px solid `--brass`, no border-radius
- Box-shadow: none (flat appearance)
- Padding: 4px 0
- Z-index: 1001

Items:
1. **New Path** — 40px tall, text 14px/1 `--brass`, padding 0 16px, no background
2. **New Test** — 40px tall, text 14px/1 `--brass`, padding 0 16px, no background
3. **New Module** — 40px tall, text 14px/1 `--brass`, padding 0 16px, no background

- Hover/tap on item: background `--brass` at 10% opacity
- Tap outside menu: closes
- Backdrop: none (menu floats directly over content)

---

## 4. Workspace Adaptation

### 4.1 Desktop (≥1024px)

- **Canvas**: infinite, scrollable both axes
- **Background**: `--bg-root` with dot grid
  - Grid dots: 40px (XL) or 32px (standard) spacing
  - Dot appearance: 1px × 1px, `--text-muted` at 15% opacity
- **Module placement**: free-form, user-draggable
- **Module sizes**:
  - Path module: 260px × 180px
  - Amplifier rack: 400px × 240px
  - Oscillator/LFO: 200px × 160px
  - Filter: 220px × 150px
  - Envelope: 240px × 170px
  - Sequencer: 480px × 200px
  - Spectrogram: 420px × 260px
  - Mixer: 360px × 200px
- **Cables**: bezier curves between output/input jacks, 2px stroke `--brass` or `--teal`
- **Module border**: 1px solid `--text-muted` at 30% opacity
- **Module header**: 32px tall, `--surface`, bottom border 1px solid `--brass` at 50% opacity

### 4.2 Tablet (768–1023px)

- **Canvas scroll**: VERTICAL ONLY — horizontal scroll is disabled (`overflow-x: hidden`)
- **Modules stack in full-width racks**
  - Each rack: width 100% of container (minus 24px padding each side), constrained to max-width 720px
  - Racks stack vertically with 16px gap between them
- **Path modules (horizontal rows)**: flex-wrap enabled
  - Wraps to 2–3 modules per row depending on individual module width
  - Each module: min-width 220px, max-width 320px, flex-grow 1
  - Row: 16px gap between modules
- **Cable rendering**: cables are absolutely positioned above modules (z-index: 10)
  - Cables follow the wrapping layout — each cable's start/end coordinates recompute based on module position in the flex wrap
  - SVG overlay layer: covers the full scrollable container height, pointer-events none
  - Cable paths use simple arcs (not bezier curves) to reduce rendering cost
- **Module sizes**: width 100% (min 300px, max 600px), height auto (content-driven)
- **Module header**: 28px tall
- **Grid dots**: visible at 24px spacing, opacity 10%

### 4.3 Phone (<768px)

- **Canvas scroll**: vertical only, single column
- **No grid dots** (--grid-dot: 0)
- **Module**: full-width card
  - Width: calc(100vw - 32px) = 16px padding left + 16px padding right
  - Margin: 8px auto
  - Height: auto (content-driven)
  - Max-width: none (stretches to fill screen)
- **Module border**: 1px solid `--text-muted` at 40% opacity
- **Module header**: 28px tall, 12px horizontal padding

#### Learning Paths as Vertical List
- Path modules no longer arranged horizontally — they stack vertically
- Each path module: full-width card with:
  - Input jack at top edge (center or left-aligned)
  - Output jack at bottom edge (center or right-aligned)
  - Cable connects output of one module to input of the next

#### Cable Visualization on Phone
- Cable between modules: vertical line running down the LEFT edge of the card stack
  - 2px solid `--brass` (for established connections)
  - 2px dashed `--text-muted` (for suggested/in-progress connections)
- Each module has:
  - Input jack: on the top-left corner of the card (8px from top, 12px from left edge)
  - Output jack: on the bottom-left corner of the card (8px from bottom, 12px from left edge)
- The cable is a straight vertical line 12px from the left edge of the container, spanning from the output jack Y-position of module N to the input jack Y-position of module N+1
- For branch connections (one output to multiple inputs): short horizontal tap (8px) from the vertical line to each connected module's input jack
- The vertical cable line is rendered as a fixed-position pseudo-element on the container, clipping to the module stack height

#### Alternative: Zigzag Cable (for complex routings)
- If a straight vertical line creates ambiguity (e.g., branches, feedback loops):
  - Cable runs down the right side of one module, crosses at midpoint to the left side of the next module
  - Only 90° elbows (no curves): `─┐` then `│` then `└─`
  - Stroke: 1.5px `--brass`, no dash
  - Z-index: 5 (behind module content, above background)

---

## 5. Patching on Phone

### 5.1 Method 1: Sequential Tapping

| Step | Visual Feedback |
|---|---|
| User taps an output jack | Jack border expands from 1px to 2.5px `--brass`, glows (no blur, just a 4px solid `--brass` ring behind jack at 30% opacity) |
| A translucent patch preview line appears | 1.5px dashed `--brass`, dash-array 4, from center of tapped jack to current finger position (or to a "follow" point if scrolling) |
| Workspace scrolls to show available input jacks | Valid input jacks briefly pulse: border expands to 2.5px `--teal` for 800ms, then settles at 2px `--teal` |
| User taps an input jack | Connection confirmed: preview line solidifies (200ms transition), dash-array removed, stroke becomes solid `--brass` (or `--teal` for CV connections) |
| User taps empty space | Preview line fades out (150ms), all jacks return to normal state |

#### Scroll Behavior During Patching
- While the preview line is active, the workspace scroll inertia is reduced by 50% to prevent accidental disengagement
- The preview line's endpoint snaps to the nearest valid input jack within 40px radius (assistive snap)

### 5.2 Method 2: Long-Press Menu

| Step | Visual Feedback |
|---|---|
| User long-presses (500ms) on an output jack | Haptic feedback (if device supports `navigator.vibrate(20)`). Jack border → 2.5px `--brass` |
| Floating menu appears | Position: 8px above the jack or 8px below (whichever fits viewport). Width: 160px. Background: `--surface`. Border: 1px `--brass`. No border-radius. |
| Menu lists nearby modules with input jacks | Max 4 items. Each item: 40px tall, padding 8px 12px, flex row: [jack icon 16×16 `--teal`] [8px gap] [module label 13px `--text-primary`]. If >4 items, last shows "+2 more" → tap to expand a sub-menu. |
| User taps an item | Connection made. Menu closes. Cable renders. |
| User taps outside menu | Menu closes. Jack returns to normal. |

#### Menu Item Highlighting
- Hover/tap on item: background `--brass` at 10% opacity
- Active item: left border 2px solid `--brass`

### 5.3 Cable Preview

- Preview line: `stroke-dasharray="4 4"`, `stroke="--brass"`, `stroke-width="1.5"`, `opacity="0.7"`
- During active patching, all valid input jacks receive a subtle indicator:
  - A 4px ring appears behind the jack: `--teal` at 20% opacity, no blur
  - The ring pulses slowly (1.5s cycle): opacity 0.2 → 0.35 → 0.2
- Connection confirmed transition:
  1. Preview line opacity → 1.0 (50ms)
  2. stroke-dasharray → 0 (100ms, smooth dash removal)
  3. stroke-width → 2px (100ms)
  4. stroke color → final color (50ms)
  5. Jack border → 1px `--text-muted` (resting state, 100ms)

---

## 6. Statistics Spectrogram on Phone

### 6.1 Spectrogram Grid

- **Cell size**: 14px × 14px (reduced from 20px on desktop)
- **Grid display**: lighter grid lines (1px, `--text-muted` at 20% opacity)
- **Color mapping**: same as desktop — frequency amplitude maps to:
  - 0–20%: `--bg-root` (no signal)
  - 21–40%: `--teal` at 60%
  - 41–60%: `--teal` at 100%
  - 61–80%: `--brass` at 70%
  - 81–100%: `--brass` at 100%
- No gradients between cells (each cell is a solid color)

### 6.2 Control Knobs

Desktop/tablet layout (vertical column of knobs to the right of spectrogram) is reflowed:

- Knobs arranged **horizontally** below the spectrogram in a single row
- Row: width 100%, height 48px, display flex, justify-content space-around
- 4 knobs (e.g., Time Range, Zoom, Frequency Focus, Gain):
  - Each: 24px diameter, border-radius 50%
  - Invisible hit area: 48px × 48px centered on each
  - Spacing: minimum 8px between hit areas
  - No labels (use tooltip on tap/hold: 12px `--text-muted`, appears above knob after 400ms)

### 6.3 Touch Interaction

#### Horizontal Time Scroll
- Swipe left/right on the spectrogram surface: scrolls time range horizontally
- Scroll momentum: 300ms deceleration
- Scroll indicators: subtle `--text-muted` arrows at left/right edges of spectrogram (8px × 8px, opacity 0.4) when content is scrollable
- Rubber-band bounce at edges: 60px max over-scroll

#### Pinch to Zoom
- Two-finger pinch on spectrogram: adjusts time range zoom
- Pinch out → zoom in (shorter time window, higher detail)
- Pinch in → zoom out (longer time window, lower detail)
- Zoom factor: range 0.25× to 4×, increments of 0.1×
- During pinch: overlay shows current zoom level as text "2.5×" centered on spectrogram, 14px `--text-primary`, fades out 1.5s after pinch ends
- Pinch replaces the "Zoom" knob entirely (zoom knob hidden on touch devices)

### 6.4 Spectrogram Height on Phone

- Height: `calc(40vh - 64px)` — fills 40% of viewport minus bottom tool case
- Min height: 160px
- Max height: 300px

---

## 7. Touch Targets

All interactive elements below the stated minimums are considered accessibility violations.

| Element | Visible Size | Invisible Hit Area (touch) | Minimum Clear Space |
|---|---|---|---|
| Knob (desktop/tablet) | 32–40px | 48px × 48px | 8px |
| Knob (phone) | 24px | 48px × 48px | 8px |
| Jack (desktop) | 12px | 40px × 40px | 8px |
| Jack (tablet/phone) | 10px | 44px × 44px | 8px |
| Icon button (top rail) | 24px | 44px × 44px | 8px |
| Icon button (bottom case) | 28px | 48px × 48px | 8px |
| Text button | content-width | 44px min height, content-width + 32px min width | 8px |
| Cable (clickable) | 2px visible | 20px (full length, 10px each side of center) | 4px |
| Avatar | 28–36px | 44px × 44px | 8px |
| Spectrogram cell | 14px | 20px × 20px (each cell is a tap target for detail drill-down) | 4px |
| Menu item | 40px tall | 44px min height, full width | 4px |

### 7.1 Implementation Notes

- Hit areas use a transparent `::before` pseudo-element with `position: absolute` and `padding` or `width`/`height` to extend beyond the visible element
- Jacks: the visible 10px circle is centered within the 44px hit area. The `::before` catch-all registers `pointer-events: auto` while the visible jack registers `pointer-events: none` to prevent double-firing
- Cables: each cable segment has a 20px invisible hit area using a wider transparent SVG path with `stroke: transparent; stroke-width: 20px; pointer-events: stroke`

---

## 8. Cross-Breakpoint Transition Rules

### 8.1 Viewport Resize Behavior

When the user resizes the viewport across breakpoints:

1. **Modules that were freely placed** (desktop) are reflowed into the rack layout in their original left-to-right, top-to-bottom order
2. **Cable connections are preserved** — the cable SVG recalculates all end-point positions on a `resize` event (debounced 150ms)
3. **Active patch sessions** are cancelled on breakpoint crossing (the user is notified via a brief toast: "Patch cancelled — layout changed")
4. **Scrolled position** resets to top on transition from desktop to tablet/phone

### 8.2 `matchMedia` Breakpoint Constants

```javascript
const BREAKPOINTS = {
  PHONE: window.matchMedia('(max-width: 767px)'),
  TABLET: window.matchMedia('(min-width: 768px) and (max-width: 1023px)'),
  DESKTOP: window.matchMedia('(min-width: 1024px)'),
};
```

### 8.3 Orientation Change (Phone)

- On orientation change from portrait to landscape, the bottom tool case height collapses to 56px (more horizontal room)
- The 5 icon buttons reflow to a single row with wider spacing
- The spectrogram on landscape phone: height increases to 55vh (more horizontal room for knobs row)
- Modules in landscape: width calc(100vw - 48px) — more padding since there is horizontal room

---

## 9. Keyboard & Mouse Considerations (Desktop Only)

### 9.1 Keyboard Navigation
- Tab order: left rail → top rail knobs → workspace modules (left-to-right, top-to-bottom) → user menu
- All interactive elements reachable via Tab
- Enter/Space: activates button, toggles connection, confirms patch
- Escape: cancels current patch preview, closes menus
- Arrow keys (when focus is on knob): increase/decrease parameter value (step 1% per press, 5% per held press after 300ms)
- Ctrl+Z: undo last cable connection
- Ctrl+Shift+Z: redo

### 9.2 Mouse Precision
- Knob hover: cursor changes to `grab`, then `grabbing` on mousedown
- Module drag: cursor changes to `move`
- Jack hover: cursor changes to `crosshair`
- Cable hover: cursor changes to `pointer`
- No custom scrollbars — use native browser scrollbars styled:
  ```css
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg-root); }
  ::-webkit-scrollbar-thumb { background: var(--text-muted); border-radius: 0; }
  ```

---

## 10. Summary of Breakpoint Differences

| Feature | Desktop (≥1024px) | Tablet (768–1023px) | Phone (<768px) |
|---|---|---|---|
| Top rail | Full, 56px, labeled knobs | Compact, 48px, icon-only nav, no knob labels | Hidden entirely |
| Navigation | Text + icons | Icons only (tooltips) | Bottom tool case icons |
| Logo | 36px | 28px | 24px (in bottom case) |
| User module | Avatar 36px + wave ring + name + dropdown | Avatar 28px + simplified ring, no name | Avatar 24px (in bottom case) |
| Workspace scroll | X + Y free | Y only | Y only |
| Module layout | Free-form floating | Full-width racks, flex-wrap rows | Single column cards |
| Grid dots | 32–40px | 24px | None |
| Cables | Bezier curves | Simple SVG arcs | Vertical line / zigzag (90° elbows) |
| Patching | Click-drag | Click-drag or tap-seq | Tap-seq or long-press menu |
| Spectrogram | 20px cells, right-side knobs | 20px cells, right-side knobs | 14px cells, bottom knobs row |
| Touch targets | 40–44px | 44–48px | 44–48px |
| Navigation type | Top rail | Top rail | Bottom tool case |
| Keyboard nav | Full Tab + arrow support | Tab support (limited) | None (touch-only) |
| Patch undo | Ctrl+Z | Ctrl+Z | None (or shake-to-undo) |
