# Layout & Navigation — General UI Framework

> **Scope**: Top Command Rail, workspace/patch bay, navigation system, base DOM hierarchy, transitions, mobile adaptation
> **Agent Dependencies**: Agent 2 (Module Library), Agent 3 (Path Builder), Agent 5 (Drag Physics), Agent 7 (Mobile)

---

## 1. Shared Token Contract (Exact Values)

All spacing, colors, and typography below are global constants. Every component in every agent's domain MUST reference these tokens — never inline values.

### 1.1 Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-root` | `#0B0B0D` | Workspace background, root body |
| `--surface` | `#16161A` | Rail, drawer, module backgrounds |
| `--brass` | `#D4A843` | Accent, active states, borders |
| `--brass-light` | `#E0B84C` | Logo hover glow (no blur, solid color) |
| `--teal` | `#3D5A5C` | Secondary accent, activity indicators |
| `--text-primary` | `#F5F0E7` | Body text, headings |
| `--text-muted` | `#8A8882` | Secondary text, idle borders |
| `--success` | `#6A8A5C` | Completion states |
| `--danger` | `#C8553D` | Destructive actions, errors |
| `--border` | `#2A2A2E` | Dividers, subtle borders |
| `--dot-grid` | `#1F1F23` | Workspace background dots |

### 1.2 Spacing Grid

- **Baseline**: 8px increments
- **Rail padding**: 16px horizontal
- **Knob gaps**: 8px
- **Rack gap (vertical)**: 24px
- **Dot grid interval**: 40px
- **Module snap grid**: 40px
- **User drawer padding**: 16px

### 1.3 Typography

| Role | Font | Weight | Size (rem) |
|------|------|--------|------------|
| Heading | IBM Plex Sans | 600 (SemiBold) | 1.25 / 1.0 |
| Body | Tajawal | 400 (Regular) | 0.875 |
| Data/Mono | JetBrains Mono | 400 | 0.8125 |
| Knob label | Tajawal | 500 | 0.625 (10px) |

### 1.4 Borders & Radii

- **Container border-radius**: `0` (2px max allowed on child elements)
- **Knob border-radius**: `50%` (only exception)
- **Default border**: `1px solid #2A2A2E`
- **Rail bottom border**: `1px solid #D4A843`
- **Knob active border**: `1.5px solid #D4A843`
- **No box-shadow with blur > 0**. Use solid-color borders only.

---

## 2. Base DOM Hierarchy

```
<body style="background: var(--bg-root); margin: 0; font-family: Tajawal, sans-serif;">
  <div id="app" style="position: relative; width: 100vw; height: 100vh; overflow: hidden;">
    <!-- 2.1 Top Command Rail -->
    <header id="command-rail">
      <div class="rail-logo"></div>
      <nav class="rail-nav-knobs">
        <div class="knob" data-section="library"></div>
        <div class="knob" data-section="paths"></div>
        <div class="knob" data-section="tests"></div>
        <div class="knob" data-section="statistics"></div>
      </nav>
      <div class="rail-user"></div>
    </header>

    <!-- 2.2 User Drawer (conditional) -->
    <div id="user-drawer" class="hidden"></div>

    <!-- 2.3 Main Workspace (Patch Bay) -->
    <main id="workspace">
      <div class="dot-grid-bg"></div>
      <div class="module-container" id="module-container">
        <!-- Modules rendered here by Agent 2, 3, etc. -->
      </div>
    </main>

    <!-- 2.4 Mobile Bottom Tool Case (hidden on desktop) -->
    <footer id="bottom-tool-case" class="md:hidden"></footer>
  </div>
</body>
```

### 2.1 Z-Index Stack

| Layer | Element | Z-Index |
|-------|---------|---------|
| Base | dot-grid-bg | 0 |
| Content | module-container, modules | 10 |
| Overlay | transition-wipe overlay | 500 |
| Drawer | user-drawer | 999 |
| Rail | command-rail | 1000 |
| Rail (children) | rail-logo, rail-nav-knobs, rail-user | 1001 |
| Tooltip | knob tooltip | 1100 |
| Mobile | bottom-tool-case | 1000 |

### 2.2 Focus Management

- Tab order: Logo → Knob[0] → Knob[1] → Knob[2] → Knob[3] → User Avatar → Drawer links
- Each knob, logo, and avatar is a `<button>` element with `tabindex` management
- When drawer is open, focus is trapped inside drawer (TAB cycles drawer items, Shift+TAB reverse, Escape closes)
- `aria-label` on each knob: `"Library section"`, `"Paths section"`, etc.
- Role `navigation` on `<nav class="rail-nav-knobs">`

---

## 3. Top Command Rail

### 3.1 Rail Container (`#command-rail`)

```
#command-rail {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: var(--surface);
  border-bottom: 1px solid var(--brass);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 8px;
  z-index: 1000;
  box-sizing: border-box;
}
```

Layout justification:
- `display: flex; align-items: center;`
- First child (logo) auto left
- Second child (nav knobs) with `margin-left: auto`
- Last child (user) with `margin-left: auto`
- Rail shrinks as needed — no min-width overflow, items can compress gap to 4px minimum

### 3.2 Rail Hover State — Logo

When user hovers over the logo specifically (not the whole rail):
- `#command-rail` border-bottom-color transitions from `#D4A843` to `#E0B84C` over 150ms
- Transition: `border-bottom-color 150ms ease`
- On mouseleave: transitions back to `#D4A843` over 300ms

### 3.3 Responsive Behavior

- **Desktop (>= 768px)**: `#command-rail` visible, `#bottom-tool-case` hidden (`display: none`)
- **Mobile (< 768px)**: `#command-rail` hidden, `#bottom-tool-case` visible (see §7)
- Medium breakpoint: 768px. Use `matchMedia('(max-width: 767px)')` for JS listeners.

---

## 4. Logo

### 4.1 Element Spec

```
.rail-logo {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  cursor: pointer;
}
```

SVG viewBox: `0 0 36 36`

### 4.2 SVG Path Description

The logo is a merged sine wave + patch jack:

- Wave: A sinusoidal path starting at `(2, 26)`, peaking at `(9, 10)`, crossing zero at `(18, 18)`, trough at `(27, 26)`, curving down-right into a circular jack hole.
- Jack circle: center `(27, 26)`, radius `4px`, filled `--bg-root` with `1.5px` `--brass` stroke.
- Wave stroke: `2px`, color `--brass`, linecap `round`.

```
<svg viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
  <path d="M2 26 C 2 10, 9 10, 9 10 C 9 10, 14 10, 18 18 C 22 26, 27 26, 27 26"
        fill="none" stroke="#D4A843" stroke-width="2" stroke-linecap="round"/>
  <circle cx="27" cy="26" r="4" fill="#0B0B0D" stroke="#D4A843" stroke-width="1.5"/>
</svg>
```

### 4.3 States

| State | Change |
|-------|--------|
| Idle | As above |
| Hover | Rail border-bottom transitions to `#E0B84C`. Logo SVG stroke becomes `#E0B84C`. Cursor: pointer. |
| Click | `history.pushState('/')` → dispatches custom event `section:change` with detail `{ section: 'default' }` → workspace renders library default view. |

### 4.4 Accessibility

- `<button class="rail-logo" aria-label="Return to library home">`
- On focus: visible `2px` solid `var(--brass)` outline with `outline-offset: 2px`

---

## 5. Navigation Knobs

### 5.1 Container

```
.rail-nav-knobs {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}
```

### 5.2 Knob Element

```
.knob {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--surface);
  border: 1.5px solid var(--text-muted);
  cursor: ns-resize; /* indicates vertical drag */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: border-color 200ms ease, background 200ms ease;
}
```

### 5.3 Knob Label

```
.knob-label {
  position: absolute;
  bottom: -16px; /* 6px gap + 10px font height = 16px below knob center */
  left: 50%;
  transform: translateX(-50%);
  font-family: Tajawal;
  font-weight: 500;
  font-size: 10px;
  color: var(--text-muted);
  white-space: nowrap;
  transition: color 200ms ease;
  pointer-events: none;
}
```

### 5.4 Indicator Line

Each knob contains an inner ring (38px diameter) with a tick mark indicator:

```
<!-- Inside each .knob -->
<svg class="knob-indicator" viewBox="0 0 40 40" width="40" height="40"
     style="position: absolute; top: 0; left: 0; pointer-events: none;">
  <line x1="20" y1="20" x2="20" y2="6"
        stroke="#D4A843" stroke-width="2" stroke-linecap="round"
        transform="rotate(0, 20, 20)" />
</svg>
```

- Line: `2px` wide, `8px` long (from `y=6` to `y=14` relative to center), centered at `(20,20)`
- The `transform: rotate(...)` is controlled via JS based on knob state.

### 5.5 Knurled Texture

Simulated with a conic-gradient on a pseudo-element:

```
.knob::before {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: 50%;
  background: repeating-conic-gradient(
    #2A2A2E 0deg 3deg,
    transparent 3deg 6deg
  );
  opacity: 0.3;
  pointer-events: none;
}
```

Note: Only visible when knob is hovered, active, or focused. Controlled via CSS:

```
.knob:hover::before,
.knob.active::before,
.knob:focus-visible::before {
  opacity: 0.5;
}
```

### 5.6 Inner Center Dot

```
.knob-center {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  transition: background 200ms ease;
  pointer-events: none;
}
```

When active: `background: var(--brass)`.

### 5.7 Full State Table

| State | Border | Indicator | Center Dot | Label Color | Knurl Opacity |
|-------|--------|-----------|------------|-------------|---------------|
| Idle | `1.5px solid #8A8882` | Hidden (`opacity: 0`) | `#8A8882` | `#8A8882` | `0` |
| Hover | `1.5px solid #D4A843` | Visible, `opacity: 0.5`, `rotate(0)` | `#8A8882` | `#D4A843` | `0.3` |
| Active (selected) | `1.5px solid #D4A843` | Visible, `opacity: 1`, `rotate(15deg)` | `#D4A843` | `#D4A843` | `0.5` |
| Focused | Hover style + `2px dotted #D4A843` at `2px` offset | Hover | Hover | Hover | `0.3` |
| Disabled | `1.5px solid #8A8882` | Hidden | `#8A8882` | `#8A8882` | `0` |
| Disabled+Active | `1.5px solid #D4A843` | Visible `opacity: 0.4`, `rotate(15deg)` | `#D4A843` | `#D4A843` | `0` |

### 5.8 Focused Style

```
.knob:focus-visible {
  outline: none;
  border-color: var(--brass);
}
.knob:focus-visible::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 1px dotted var(--brass);
  pointer-events: none;
}
```

### 5.9 Interaction Model

**Click / Keyboard Enter / Space**
- If the knob is not already active, set it active. Deactivate all other knobs.
- `rotateKnob(knobElement, 15)` — animate SVG indicator from current rotation to 15deg over 200ms.
- Dispatch `section:change` event.

**Vertical Drag (pointer events)**
1. On `pointerdown` on knob: capture pointer, store `startY`, store `currentSection` index.
2. On `pointermove`: calculate delta `dy = startY - event.clientY`. Each `40px` of drag = 1 section change. Clamp to 0–3 range.
3. On `pointerup`: release pointer capture. Snap to nearest section index.
4. During drag: update tooltip content in real time (see §5.10).

**Scroll Wheel**
1. `wheel` event on knob with `deltaY` aggregation: accumulate `deltaY`. Each `100` units = 1 section change.
2. Debounce at 200ms. On threshold crossed: change section, reset accumulator.

**Touch Equivalent**
- `touchstart` / `touchmove` / `touchend` — same logic as pointer events.
- Prevent default on `touchmove` to avoid page scroll during knob interaction.

### 5.10 Numeric Tooltip

```
.knob-tooltip {
  position: fixed; /* relative to viewport */
  top: calc(var(--knob-top) - 36px); /* 36px above knob center */
  left: calc(var(--knob-left) + 20px); /* centered above knob */
  transform: translateX(-50%);
  background: var(--surface);
  border: 1px solid var(--brass);
  padding: 4px 10px;
  font-family: JetBrains Mono;
  font-size: 11px;
  color: var(--text-primary);
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 150ms ease;
  z-index: 1100;
}
.knob-tooltip.visible { opacity: 1; }
```

Tooltip content format: `"Library · 1/4"`, `"Paths · 2/4"`, `"Tests · 3/4"`, `"Statistics · 4/4"`
Section index mapping: `0 → Library`, `1 → Paths`, `2 → Tests`, `3 → Statistics`

Lifecycle:
- Appears on first interaction (drag start, click, wheel tick)
- Remains visible during interaction
- After interaction ends (pointerup, wheel debounce timeout, 500ms after last event), fades out over 500ms
- Use `opacity` only (no transform) to avoid layout shift

### 5.11 Accessibility

- Each knob is `<button class="knob" role="tab" aria-selected="false" aria-label="Library section" tabindex="0">`
- Active knob: `aria-selected="true"`
- `<nav class="rail-nav-knobs" role="tablist" aria-label="Workspace sections">`
- Knob labels: use `aria-labelledby` or visually hidden `<span>` with `aria-label`
- Focus indicator: see §5.8

### 5.12 Disabled Knobs

Some sections may be locked behind feature gates (e.g., "Tests" requires assessment setup). Apply via:
```
.knob[data-disabled="true"] {
  opacity: 0.4;
  pointer-events: none;
}
```
Disabled knobs remain visible but non-interactive. Active section can still be disabled if the user navigates away and back.

---

## 6. User Module (Far Right)

### 6.1 Container

```
.rail-user {
  position: relative;
  margin-left: auto;
  flex-shrink: 0;
}
```

### 6.2 Avatar + Wave Ring

```
<div class="rail-user" role="button" tabindex="0" aria-label="Open user menu">
  <svg class="user-wave-ring" width="36" height="36" viewBox="0 0 36 36">
    <!-- Oscilloscope wave trace -->
    <path class="wave-path" d="M4 18 Q8 14 12 18 T20 18 T28 18 T32 18"
          fill="none" stroke="#3D5A5C" stroke-width="1.5" stroke-linecap="round"/>
    <!-- Avatar circle clipped to 32px -->
    <clipPath id="avatar-clip">
      <circle cx="18" cy="18" r="16"/>
    </clipPath>
    <image href="/avatars/default.png" x="2" y="2" width="32" height="32"
           clip-path="url(#avatar-clip)" />
  </svg>
</div>
```

- Outer SVG: 36x36px
- The wave path animates continuously as a pulsing trace:
  - CSS animation `wave-pulse` on `.wave-path`: alternates between two path shapes (subtle Y-offset) over 2s ease-in-out infinite.
  - `stroke-dashoffset` animation creates a scanning-line effect: `stroke-dasharray: 10 20` animating offset from 0 to 30 over 3s linear infinite.
- The avatar image is 32x32 clipped to circle.

### 6.3 Avatar Wave Animation

```
@keyframes wave-pulse {
  0%   { d: path("M4 18 Q8 14 12 18 T20 18 T28 18 T32 18"); }
  50%  { d: path("M4 18 Q8 12 12 18 T20 16 T28 19 T32 18"); }
  100% { d: path("M4 18 Q8 14 12 18 T20 18 T28 18 T32 18"); }
}
@keyframes wave-scan {
  from { stroke-dashoffset: 0; }
  to   { stroke-dashoffset: -30; }
}
.wave-path {
  animation: wave-pulse 2s ease-in-out infinite, wave-scan 3s linear infinite;
}
```

Note: If CSS `d:` path animation is not supported, use SMIL `<animate>` instead.

### 6.4 States

| State | Change |
|-------|--------|
| Idle | Wave animates normally, avatar visible |
| Hover | `cursor: pointer`. Wave stroke becomes `var(--brass)` for 300ms then fades back. Tooltip "Profile & Settings" appears above. |
| Focus | `outline: 2px solid var(--brass)` with `outline-offset: 2px` |
| Click / Enter | Toggles `#user-drawer` visibility |

---

## 7. User Drawer

### 7.1 Container

```
#user-drawer {
  position: fixed;
  top: 56px; /* flush with bottom of rail */
  right: 0;
  width: 360px;
  max-width: calc(100vw - 32px); /* 16px padding on each side */
  background: var(--surface);
  border-bottom: 1px solid var(--brass);
  border-left: 1px solid var(--border);
  z-index: 999;
  padding: 16px;
  box-sizing: border-box;
  transform: translateY(-100%);
  opacity: 0;
  transition: transform 250ms ease-out, opacity 200ms ease;
  pointer-events: none;
}
#user-drawer.open {
  transform: translateY(0);
  opacity: 1;
  pointer-events: auto;
}
```

Drawer slides down from the top of the workspace (not from side). TL;DR: it drops down from the rail like a scope hood.

### 7.2 Drawer Content Structure

```
<div id="user-drawer">
  <!-- Profile Card -->
  <div class="drawer-profile">
    <img class="drawer-avatar" src="..." width="48" height="48" style="border-radius: 50%;" />
    <div class="drawer-name">Zuhair Ahmed</div>
    <div class="drawer-email">zuhair@example.com</div>
  </div>

  <!-- Divider -->
  <hr class="drawer-divider" />

  <!-- Module Links -->
  <nav class="drawer-links">
    <button class="drawer-link" data-action="settings">
      <span class="drawer-icon"><!-- gear SVG --></span>
      <span>Settings</span>
    </button>
    <button class="drawer-link" data-action="notifications">
      <span class="drawer-icon"><!-- bell SVG + LED --></span>
      <span>Notifications</span>
      <span class="drawer-led"></span>
    </button>
    <button class="drawer-link" data-action="theme">
      <span class="drawer-icon"><!-- sun/moon SVG --></span>
      <span>Theme</span>
      <div class="drawer-toggle-knob"><!-- mini knob 20px --></div>
    </button>
    <button class="drawer-link logout" data-action="logout">
      <span class="drawer-icon"><!-- power SVG --></span>
      <span>Logout</span>
    </button>
  </nav>
</div>
```

### 7.3 Drawer Link Spec

```
.drawer-link {
  display: flex;
  align-items: center;
  width: 100%;
  height: 40px;
  padding: 0 8px;
  background: transparent;
  border: none;
  border-left: 2px solid transparent;
  color: var(--text-primary);
  font-family: Tajawal;
  font-size: 14px;
  cursor: pointer;
  transition: border-left-color 150ms ease, background 150ms ease, color 150ms ease;
}
.drawer-link:hover {
  border-left-color: var(--brass);
  background: rgba(212, 168, 67, 0.08);
}
.drawer-link.logout:hover {
  border-left-color: var(--danger);
  color: var(--danger);
  background: rgba(200, 85, 61, 0.08);
}
```

### 7.4 Drawer Divider

```
.drawer-divider {
  border: none;
  height: 1px;
  background: var(--border);
  margin: 12px 0;
}
```

### 7.5 Drawer Icons

All icons: 20x20px, stroke `var(--text-muted)`, 1.5px stroke-width, round linecap.

- **Settings (gear)**: 20x20 circle with 8 spokes, center hole 4px
- **Notifications (bell)**: Bell body (trapezoid) + clapper (circle)
- **Theme (sun/moon)**: 20x20 circle; sun has 8 rays outside, moon is crescent
- **Logout (power)**: Circle with vertical gap at top, line exiting to right

**Notifications LED indicator**: A `6px` circle at the right edge of the notification link, `--danger` color, visible when unread count > 0.

### 7.6 Theme Toggle Knob

A mini circular knob (20px diameter) inside the theme row:
```
.drawer-toggle-knob {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid var(--text-muted);
  background: var(--surface);
  margin-left: auto;
  position: relative;
  transition: border-color 200ms;
}
.drawer-toggle-knob.active {
  border-color: var(--brass);
}
/* 8px indicator line */
.drawer-toggle-knob::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 9px;
  width: 2px;
  height: 6px;
  background: var(--brass);
  border-radius: 1px;
  transform: rotate(var(--theme-rotation, 0deg));
  transition: transform 300ms ease;
}
```

- Light theme: `--theme-rotation: 0deg` (indicator up)
- Dark theme: `--theme-rotation: 180deg` (indicator down)

### 7.7 Drawer Lifecycle

- **Open**: Click avatar OR programmatic call `openUserDrawer()`. Add class `open`. Focus trap activates.
- **Close triggers**: Click outside drawer, press Escape, click a link (navigates), click avatar again
- **Close animation**: `translateY(-100%)` over 250ms ease-out, opacity fades over 200ms
- **Overlay**: A translucent overlay (`rgba(0,0,0,0.4)`) covers the workspace behind the drawer, z-index 998. Clicking it closes the drawer.
- Focus trap: TAB cycles through `.drawer-link` items only. First/last element wraps.

---

## 8. Workspace (Patch Bay)

### 8.1 Container

```
#workspace {
  position: absolute;
  top: 56px; /* below rail */
  left: 0;
  right: 0;
  bottom: 0;
  overflow: auto;
  background: var(--bg-root);
}
```

### 8.2 Dot Grid Background

```
.dot-grid-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  min-height: 100%;
  background-image: radial-gradient(circle, var(--dot-grid) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}
```

- Dots: 1px diameter, color `#1F1F23`
- Spacing: 40px x 40px grid

### 8.3 Module Container

```
.module-container {
  position: relative;
  z-index: 10;
  min-height: 100%;
  padding: 24px 16px; /* 24px top to clear rail, 16px sides */
}
```

Modules within this container use `position: absolute` with `left`/`top` values snapped to 40px grid.

Snap formula: `snapped = Math.round(position / 40) * 40`

### 8.4 Rack Stacking

Modules can nest into horizontal "racks" — rows of related modules:
- A rack is a `<div class="rack">` with `display: flex; gap: 16px; flex-wrap: wrap;`
- Racks stack vertically with `24px` gap between them.
- Each rack is a block-level element; modules inside are inline-flex children.
- Racks are positioned absolutely within `.module-container`.

```
.rack {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  width: 100%;
}
.rack + .rack {
  margin-top: 24px;
}
```

### 8.5 Scroll Behavior

- Infinite scroll: workspace content extends beyond viewport; user scrolls naturally via browser scroll.
- No virtual scrolling (simplicity). Content height grows as modules are added.
- Scroll position is NOT preserved across section changes (each section has its own module layout).

### 8.6 Drag-and-Drop (Foundation)

See Agent 5 for full physics. This spec defines the snap contract:
1. All modules have `data-x` and `data-y` attributes in grid units (40px multiples).
2. On drag end, position MUST snap to nearest 40px multiple.
3. Module dimensions are also in 40px multiples.
4. Drag handles are 8px circles at the top-left corner of each module.

---

## 9. Navigation Transitions

### 9.1 Wipe Effect

When a knob is activated and section changes:

1. Dispatch `section:change` event with `{ from: 'library', to: 'paths' }`
2. A wipe overlay is created:

```
<div id="wipe-overlay" style="
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 500;
  pointer-events: none;
  overflow: hidden;
">
  <div class="wipe-old" style="...">  <!-- old content slides left -->
  <div class="wipe-new" style="...">  <!-- new content slides from right -->
</div>
```

3. Animation:
   - `wipe-old`: `translateX(0)` → `translateX(-100%)` over 300ms
   - `wipe-new`: `translateX(100%)` → `translateX(0)` over 300ms
   - Both use `transition: transform 300ms ease-out`

4. During transition:
   - An invisible overlay (`pointer-events: none` on wipe, but also a `pointer-events: auto` blocker on `#workspace` to prevent interaction)
   - Actually: set `#workspace { pointer-events: none; }` for 300ms

5. After transition (300ms):
   - Remove wipe-overlay DOM elements
   - Set `#workspace { pointer-events: auto; }`
   - New modules are now rendered in `#module-container`

### 9.2 Implementation Strategy

```
function changeSection(targetSection) {
  if (isTransitioning) return;
  isTransitioning = true;

  const fromSection = currentSection;

  // 1. Capture snapshot of current modules as DOM
  // 2. Inject new modules into module-container (but hidden)
  // 3. Create wipe overlay with snapshots
  // 4. Animate wipe
  // 5. On transitionend: cleanup, set pointer-events
  // 6. Update knob states
  // 7. history.pushState(...)

  currentSection = targetSection;
  isTransitioning = false;
}
```

### 9.3 History Management

- Each section change pushes state: `history.pushState({ section: 'paths' }, '', '/paths')`
- Back/forward: listen to `popstate` event. Compare `event.state.section` to current. If different, trigger `changeSection` WITHOUT pushState.
- URL paths: `"/"`, `"/paths"`, `"/tests"`, `"/statistics"`

### 9.4 Performance Note

- Pre-render all 4 section module sets in hidden containers (or use `display: contents` swapping).
- Alternatively, lazy-render: create section content on first visit, cache in a `Map<section, HTMLElement>`, re-insert on subsequent visits.
- Avoid re-rendering from scratch on repeat navigation.

---

## 10. Mobile Bottom Tool Case

### 10.1 Container

```
#bottom-tool-case {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--surface);
  border-top: 1px solid var(--brass);
  display: none; /* hidden on desktop */
  align-items: center;
  justify-content: space-around;
  padding: 0 12px;
  z-index: 1000;
}
```

### 10.2 Mobile Breakpoint

```
@media (max-width: 767px) {
  #command-rail { display: none; }
  #bottom-tool-case { display: flex; }
  #workspace { top: 0; bottom: 64px; }
  #user-drawer { top: 0; }
}
```

### 10.3 Bottom Tool Case Content

```
<div id="bottom-tool-case">
  <!-- 4 section icon buttons, 28x28px -->
  <button class="tool-btn" data-section="library" aria-label="Library">
    <!-- library icon SVG -->
  </button>
  <button class="tool-btn" data-section="paths" aria-label="Paths">
    <!-- paths icon SVG -->
  </button>

  <!-- Center: Large create button -->
  <button class="tool-btn create-btn" aria-label="Create new path">
    <!-- patch jack icon -->
  </button>

  <button class="tool-btn" data-section="tests" aria-label="Tests">
    <!-- tests icon SVG -->
  </button>
  <button class="tool-btn" data-section="statistics" aria-label="Statistics">
    <!-- statistics icon SVG -->
  </button>

  <!-- User avatar (28px) replaces rightmost user module -->
  <button class="tool-btn user-btn" aria-label="User menu">
    <img src="/avatars/default.png" width="28" height="28"
         style="border-radius: 50%;" />
  </button>
</div>
```

### 10.4 Tool Button Spec

```
.tool-btn {
  width: 28px;
  height: 28px;
  border-radius: 2px; /* 2px max, not 50% */
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 200ms ease, color 200ms ease;
}
.tool-btn:hover,
.tool-btn.active {
  border-color: var(--brass);
  color: var(--brass);
}
.create-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%; /* only circular element */
  border: 2px solid var(--brass);
  background: var(--surface);
}
.create-btn:hover {
  background: rgba(212, 168, 67, 0.1);
}
```

### 10.5 Mobile Interactions

- Tap a tool-btn: navigates to section (same as desktop knob click)
- Center create button: opens path creation wizard (Agent 6 detail)
- User button: opens user drawer (same as desktop, but drawer position starts from `top: 0` — no rail to offset)
- No vertical drag on mobile (tap-only for nav)
- Swipe left/right on workspace: gesture-based section switch (optional enhancement for Agent 7)

---

## 11. Event Bus

A shared custom event bus for cross-agent communication:

| Event | Detail | Dispatched By | Consumed By |
|-------|--------|---------------|-------------|
| `section:change` | `{ section: string, from: string }` | Knob click/Logo click | Agents 2,3,4,7 |
| `drawer:open` | `{}` | User avatar click | Agent 7 (mobile) |
| `drawer:close` | `{}` | Drawer close | Agent 7 |
| `theme:toggle` | `{ theme: 'light' \| 'dark' }` | Theme toggle in drawer | All agents |
| `module:drag-start` | `{ id, x, y }` | Agent 5 drag init | Agent 5 |
| `module:drag-end` | `{ id, x, y }` | Agent 5 drag end | Agents 2,3 |
| `workspace:resize` | `{ width, height }` | Window resize | All agents |

All events dispatched on `document`. Standard `new CustomEvent(name, { detail })`.

---

## 12. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `1` | Switch to Library |
| `2` | Switch to Paths |
| `3` | Switch to Tests |
| `4` | Switch to Statistics |
| `Ctrl+K` | Open command palette (future) |
| `Escape` | Close drawer / cancel drag |
| `Tab` | Cycle focus through rail items |

---

## 13. CSS Custom Properties (Complete Set)

```
:root {
  --bg-root: #0B0B0D;
  --surface: #16161A;
  --brass: #D4A843;
  --brass-light: #E0B84C;
  --teal: #3D5A5C;
  --text-primary: #F5F0E7;
  --text-muted: #8A8882;
  --success: #6A8A5C;
  --danger: #C8553D;
  --border: #2A2A2E;
  --dot-grid: #1F1F23;

  --font-heading: 'IBM Plex Sans', sans-serif;
  --font-body: 'Tajawal', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 40px;

  --rail-height: 56px;
  --knob-size: 40px;
  --knob-gap: 8px;
  --grid-unit: 40px;
  --transition-fast: 150ms;
  --transition-medium: 200ms;
  --transition-slow: 300ms;
}
```

---

## 14. Implementation Checklist

- [ ] HTML element IDs match spec exactly (`#command-rail`, `#workspace`, `#user-drawer`, `#module-container`, `#bottom-tool-case`)
- [ ] CSS custom properties defined in `:root`
- [ ] Dot grid background implemented with `radial-gradient`
- [ ] Rail: fixed position, 56px, flex layout, brass bottom border
- [ ] Logo: 36px SVG with wave+jack, click returns to library
- [ ] Knobs: 40px circular, 4 states (idle/hover/active/focused), dashed conic knurl
- [ ] Indicator line rotation (0° idle, 15° active)
- [ ] Vertical drag + scroll wheel interaction on knobs
- [ ] Numeric tooltip with 500ms fadeout
- [ ] User module: 36px SVG wave ring + 32px avatar, wave animation
- [ ] User drawer: 360px, slides from top, 4 links, focus trap
- [ ] Theme toggle: mini knob in drawer, rotates 180°
- [ ] Section transitions: horizontal wipe 300ms, pointer-events block
- [ ] History API: pushState + popstate
- [ ] Mobile: bottom tool case replaces rail at 767px breakpoint
- [ ] Disabled knob state: opacity 0.4, no hover effects
- [ ] Module snap-to-grid: 40px via Math.round
- [ ] Rack spacing: 24px vertical gap
- [ ] Event bus: all 8 events implemented
- [ ] Keyboard shortcuts: 1-4 for sections, Escape for drawer
