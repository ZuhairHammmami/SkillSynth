# Admin Central Laboratory — Complete Specification

> **Design Paradigm**: Modular analog synthesizer. Every admin function is a module you can grab, patch, and modulate. No traditional CRUD tables, forms, or dropdowns. All interaction is direct manipulation — drag, patch, twist knobs.

---

## Design Tokens (Global Overrides for Lab)

```css
:root {
  --bg-root: #0B0B0D;
  --surface: #16161A;
  --brass: #D4A843;
  --teal: #3D5A5C;
  --text-primary: #F5F0E7;
  --text-muted: #8A8882;
  --success: #6A8A5C;
  --danger: #C8553D;
  --lab-border: #2A2A2E;
  --chamfer-size: 2px;
}
```

- Spacing grid: 8px base unit
- Borders: 1px solid `var(--lab-border)` unless overridden
- Border-radius on containers: `2px` maximum (hard corners preferred)
- All radii on controls (knobs): `50%` (circular)
- No gradients anywhere. No neon glow. No glassmorphism. No soft shadows.
- No border-radius > 2px on containers.

---

## 1. Global Module Bank (Floating Library Panel)

### 1.1 Position & Trigger

| Property | Value |
|---|---|
| Anchor | Pinned top-left of workspace, 8px below the admin rail |
| Trigger | "Library" button — 32px × 32px, `--surface` bg, 1px `--lab-border` |
| Trigger icon | Small module silhouette (4-pin jack icon, 16px, `--brass`) |
| Trigger label | "Library" — 9px, `--text-muted`, `font-mono`, positioned right of icon |
| Hover state | Border shifts to `--brass` (200ms) |
| Click state | Border shifts to `--brass`, bg shifts to `#1E1E24` (50ms) |

### 1.2 Panel Sizing & Appearance

| Property | Value |
|---|---|
| Width | 300px (no shrink, no grow) |
| Max-height | 500px (overflow scroll below) |
| Background | `--surface` |
| Border | 1px solid `--lab-border` |
| Chamfer | `--chamfer-size` via clip-path: `polygon(2px 0%, 100% 0%, 100% 100%, 0% 100%, 0% 2px)` |
| Shadow | None (flat) |
| Z-index | 50 |
| Positioning | `fixed`, left: `8px` below header rail, top: `48px` (or dynamic from rail height) |

### 1.3 Panel Header

- 36px tall, horizontal divider 1px `--lab-border` at bottom
- Left: "Module Library" — 11px, `--text-primary`, `font-mono`, font-weight 500
- Right: Close icon (X) — 16px × 16px, `--text-muted`, hover `--brass`, 200ms transition
- Clicking X or clicking outside the panel boundaries closes it (200ms fade-out, `opacity: 0`)

### 1.4 Tab Row

- 40px tall, no bottom border
- Tabs: [Courses] [Tests] [Certificates] [Users] [Roles]
- Each tab: 60px × 24px, 1px `--lab-border`, bg `transparent`, 9px text `--text-muted`, `font-mono`, uppercase
- Active tab: text `--brass`, bg `#1E1E24`, border-bottom 1px `--brass`
- Hover tab: text `--brass`, border-bottom 1px `--brass` at 50% opacity
- Tab click: instant switch (no transition), content area re-renders

### 1.5 Content Modules (Draggable Cards)

- Rendered in a grid: 3 columns, 8px gap, padding `8px`
- Each card: 80px × 80px, `#1A1A20` bg, 1px `--lab-border` border
- Card content:
  - Top-left: Genre/type icon (20px × 20px) — e.g., book for course, checkmark for test, certificate icon, person for users, shield for roles — `--text-muted`
  - Center: Short label (max 10px width) — truncated with ellipsis, 8px, `--text-muted`, `font-mono`, centered
  - Right edge: Output jack — 6px diameter circle, `--brass` bg, centered vertically at right edge (4px inset from edge)
- Hover: border `--brass`, bg `#222228`, cursor `grab`
- Active drag: border `--brass`, bg `#222228`, cursor `grabbing`, opacity `0.85`
- **Drag behavior**: `data-transfer` carries module ID + type + tab origin. On drop into workspace (or into a Path module), clone the module data (not move). Original remains in library.

### 1.6 Library Empty State

- When a tab has no modules: centered text "No modules" — 10px, `--text-muted`, `font-mono`
- Loading state: three 80px × 80px skeleton rectangles, bg `#1E1E24`, with a brief opacity pulse (0.4→0.6, 800ms)

---

## 2. Building a Learning Path (Patch Builder)

### 2.1 Step 1: Create Path Module

- Admin drags the "Path" module from Library → drops onto workspace
- **Path Module container**:
  - Width: 800px default (resizable via drag handle on right edge — 8px wide invisible zone)
  - Min-width: 400px
  - Height: 200px default (auto-expands as modules are added, min 200px, max none)
  - Background: `--surface`
  - Border: 1px solid `--brass` (indicates active editing)
  - Border chamfered (2px)
- **Path Module Header** (top 36px):
  - Left: Editable "Path Name" text — click to edit, 16px, `--brass`, `font-mono`, font-weight 500
  - Editing: input field appears inline (no popup), same styling, bg `#1A1A20`, 1px `--brass` bottom border, `caret-color: --brass`
  - Press Enter or blur → commit name. Press Escape → revert.
  - Right: Module count badge — 16px × 16px, `#1E1E24` bg, 1px `--lab-border`, 8px `--text-muted` `font-mono` text (e.g., "3")
  - Far right: Delete path button — X icon, 12px, `--danger`, hidden until hover on header, 100ms fade
- **Drop zone** (below header, `calc(100% - 36px)`):
  - Accepts drops from Library module cards
  - Visual feedback on dragover: border dashes (2px dashed `--brass`, 50% opacity) around inner drop zone, 150ms
  - On drop: module card is cloned into the path

### 2.2 Step 2: Add Content Modules

- Modules inside the Path auto-arrange horizontally (left to right, LTR always regardless of page dir)
- **Module dimensions inside path**: 200px × 120px
- **Gap between modules**: 16px (fixed, not flex-based variable)
- **Module card appearance inside path**:
  - Background: `#1A1A20`
  - Border: 1px solid `--lab-border`
  - No chamfer (rectangular)
  - Content:
    - Top 16px: Genre icon (14px), right-aligned
    - Center: Title — 10px, `--text-primary`, `font-mono`, centered, max 2 lines, overflow hidden
    - Bottom-left: Input jack (6px diameter, `--teal` bg, inset 4px from left edge, centered vertically in bottom 24px zone)
    - Bottom-right: Output jack (6px diameter, `--brass` bg, inset 4px from right edge)
  - Hover: border 1px `--brass` (200ms)
- **Overflow behavior**: If modules exceed path width, a horizontal scrollbar appears (6px height, `--lab-border` track, `--brass` thumb)
- **Module removal**: Click a module inside path + press Delete key → module fades out (150ms) → path reflows (200ms)
  - Confirmation: small indicator at module top-right — trash icon (10px, `--danger`, 50% opacity, full opacity on hover) — click to delete

### 2.3 Step 3: Patching (Connecting Modules)

#### 2.3.1 Initiation

- Click on a module's **output jack** (right edge, `--brass` circle, 6px)
- Jack highlights on click: bg changes to `--text-primary`, scale 1.3 (100ms)
- A cable appears starting from output jack center
- **Cable rendering**:
  - SVG `<path>` with cubic Bézier curve (`C` command)
  - Control points: horizontal from output jack for 40px, then curve to input jack
  - Color: `--brass`, 2px stroke width
  - `fill: none`
  - Cable follows cursor until dropped
  - While following: cable endpoint snaps to cursor position, with a small 6px circle `--teal` at the cursor tip (indicating "looking for input")

#### 2.3.2 Connection

- When cursor hovers over a valid **input jack** (left edge, `--teal` circle, 6px):
  - Input jack scales to 1.4x, bg brightens to `#5A8A8C` (100ms)
  - Cable preview snaps to input jack center
  - Release mouse → connection established
  - Invalid drop (no input jack): cable disintegrates (200ms particle effect — 8 small `--brass` dots fly outward, opacity 1→0)
  - Self-connection (output to own input): cable dissolves immediately, no connection

#### 2.3.3 Connected State

- **Cable**: Solid `--brass`, 2px, Bézier curve between output and input centers
- **Pulse animation**: opacity oscillates 0.8→1.0→0.8 over 1.5s (`ease-in-out`), infinite loop
- **Padlock icon**: Appears at cable midpoint (cable parameter `t=0.5`)
  - Lock icon: 10px × 10px, `--teal`, 50% opacity, centered on cable midpoint
  - Represents locked sequencing order
  - Hover on padlock: tooltip "Sequence lock" — 8px text, `--text-muted`, `font-mono`, 100ms delay
- **Selection**: Click on cable (within 6px of centerline) → brightens to `#E0B84C`, stroke-width 2.5px, padlock turns `--brass`
- **Deletion**: Double-click a selected cable → particle disintegration effect
  - 200ms animation: cable breaks into 12 segments, each fades and drifts outward
  - After animation: connection removed, modules' jacks reset to unconnected state

#### 2.3.4 Empty Workspace State

- When no path module exists: workspace shows centered text "Drag a Path module from the Library to begin" — 12px, `--text-muted`, `font-mono`
- Dashed border (`2px dashed --lab-border`) surrounds workspace as visual cue

### 2.4 Step 4: Pass Threshold (Voltage Control)

#### 2.4.1 Opening Threshold Popup

- Single-click on a connected **cable** (selected state) → threshold popup appears
- Popup position: Floating 8px above the cable midpoint, left-aligned with midpoint
- Prevents covering the cable; if off-screen, repositions below instead

#### 2.4.2 Popup Module

| Property | Value |
|---|---|
| Width | 200px |
| Height | 100px |
| Background | `--surface` |
| Border | 1px `--lab-border` |
| Chamfer | 2px |
| Z-index | 60 |
| Close method | Click anywhere outside, or press Escape (150ms fade-out) |

#### 2.4.3 Popup Contents

- **Title**: "Threshold" — 8px `--brass`, `font-mono`, uppercase, positioned top-left, 4px padding
- **Knob**: 32px diameter, `--teal` bg (unselected portion), knob indicator `--brass` (selected portion)
  - Rotation: maps to 0°–270° range (bottom-left = 0%, bottom-right = 100%)
  - Drag up/down to adjust (vertical drag: 1px = 1% change)
  - Values snap to integer percentages

- **Value display**: Right of knob, "70%" — 14px, `JetBrains Mono`, `--text-primary`
  - When value is 0: display "0%" in `--text-muted` (no threshold)
  - When value > 0: display in `--text-primary`

- **Apply button**: Text-only "APPLY" — 8px, `--brass`, `font-mono`, `cursor: pointer`
  - Hover: text brightens to `#E0B84C`
  - Click: commits threshold value, popup closes (150ms)
  - No background, no border, no padding beyond 4px

#### 2.4.4 Cable Voltage Label

- After threshold is applied, a label appears on the cable
- **Position**: Directly below cable midpoint, offset 4px down
- **Text**: "≥70%" — 9px, `--teal`, `font-mono`
- Updates live when threshold changes
- If threshold = 0: label is hidden
- Label survives page reload (persisted to path_step_connections in DB)

#### 2.4.5 Multiple Thresholds

- A single module can have multiple outgoing cables (one output jack → multiple input jacks) — fan-out
  - Output jack shows a small "1→n" badge (8px, `--brass`, top-right of jack)
- A single input jack can accept only one incoming cable — fan-in prohibited
  - Dropping a second cable onto an occupied input jack: the new cable replaces the old (old cable disintegrates, new locks in)

---

## 3. Test Editor — Wave Shaper

### 3.1 Entering Waveform Workspace

- Admin double-clicks a Test module inside a Path (or in the Library, if "Edit" mode)
- Workspace transitions: entire content area below the action rail becomes the waveform editor
- Transition: 200ms crossfade (opacity 0→1)
- Breadcrumb at top (8px below rail): "Library > Path > Test: <test_name>" — 9px, `--text-muted`, `font-mono`, clickable segments navigate back

### 3.2 Waveform Editor Canvas

| Property | Value |
|---|---|
| Width | `100%` of available workspace |
| Height | 400px (fixed) |
| Background | `--bg-root` |
| Border | 1px `--lab-border` |
| Overflow | Hidden (no scroll within canvas) |

#### 3.2.1 Wave Baseline

- Horizontal line across the full width of the canvas at `y = 200px` (vertical center)
- Color: `--teal`, 1.5px stroke
- This line represents baseline difficulty (50th percentile)
- Nodes above = harder, below = easier

### 3.3 Wave Nodes (Questions)

#### 3.3.1 Node Appearance

| Property | Value |
|---|---|
| Diameter | 48px |
| Background | `--surface` |
| Border | 1.5px solid `--brass` |
| Border-radius | 50% |
| Cursor | `grab` (idle), `grabbing` (drag) |

- Each node displays:
  - Center: Question number (1, 2, 3…) — 12px, `--text-primary`, `font-mono`
  - Bottom edge (outside circle, 2px below): Difficulty label — "Easy" / "Med" / "Hard" — 7px, `--text-muted`, `font-mono` (auto-calculated from Y position)
- Nodes are connected by a horizontal `--teal` line, 1.5px, passing through each node's center

#### 3.3.2 Node Y-Position ↔ Difficulty Mapping

| Y Position (from top, px) | Difficulty | Color hint on node border |
|---|---|---|
| 0–80 | Hard (80–100%) | `--danger` tint on brass |
| 81–160 | Medium-Hard (60–80%) | `--brass` full |
| 161–240 | Medium (40–60%) | `--brass` |
| 241–320 | Medium-Easy (20–40%) | `--teal` tint on brass |
| 321–400 | Easy (0–20%) | `--teal` |

#### 3.3.3 Adding Nodes

- **Via button**: "Add Node" button at the end of the wave (rightmost position, after the last node)
  - Button: 48px diameter circle, dashed 1.5px `--lab-border`, bg `transparent`
  - Center: "+" icon, 14px, `--text-muted`
  - Hover: border `--brass`, `+` turns `--brass`, 200ms
  - Click: new node appears 80px to the right of the last node, at Y=200 (baseline), renumbers all nodes
- **Via double-click**: Double-click on empty canvas space → node created at that X/Y position
  - X snaps to nearest 80px grid column
  - Minimum gap between nodes: 80px
  - If X < 40px from left edge: node placed at X=80

#### 3.3.4 Moving Nodes

- **Horizontal drag** (X axis):
  - Nodes snap to 80px grid columns as they move
  - Adjacent nodes shift to maintain minimum 80px spacing (push right or pull left)
  - Connections (teal line) redraw smoothly during drag (60fps)
- **Vertical drag** (Y axis):
  - Free movement, no snap
  - Y position maps linearly to difficulty (0px top = 100% difficulty, 400px bottom = 0%)
  - Difficulty value updates live (label changes during drag)
- **Bounds**: X: 40px–canvasWidth, Y: 4px–396px (4px padding from edges)

#### 3.3.5 Deleting Nodes

- Drag the node outside the canvas area (any edge)
- Visual: node fades out over 200ms, scale 1→0.5, opacity 1→0
- If drop occurs outside canvas during drag: node is removed
- Remaining nodes renumber, wave line redraws (200ms)
- Cannot delete if only 1 node remains (delete action denied with subtle shake animation)

#### 3.3.6 Node Connection Line

- The `--teal` horizontal line passes through the center of each node
- Line redraws on every node add/remove/move (smooth transition, 200ms)

### 3.4 Node Properties Panel

#### 3.4.1 Opening

- Click a node (not drag, just click) → right-side panel slides in
- Panel width: 280px
- Background: `--surface`
- Border-left: 1px solid `--lab-border`
- Height: matches editor height (400px)
- Slides in: 200ms, translateX from `280px` to `0`
- Close: Click X top-right, or click another node (panel swaps content), or click empty canvas space (panel slides out)

#### 3.4.2 Panel Content Layout

Padding: 16px all around. Vertical stack, 16px gap between controls.

##### 3.4.2.1 Question Header

- "QUESTION 3" — 10px, `--brass`, `font-mono`, uppercase

##### 3.4.2.2 Signal Input Strip (Question Text)

- Horizontal groove: 100% width, 32px height, `--bg-root` bg, 1px `#1A1A20` inset border
- Cursor: vertical `--brass` line (2px wide) blinking at 1s interval
- Text appears: 11px, `--text-primary`, `font-mono`
- Click to focus; type to set question text
- Placeholder when empty: "Signal input…" — 11px, `--text-muted`, `font-mono`

##### 3.4.2.3 Type Knob

- Knob diameter: 24px
- Values:
  - 0°: Multiple Choice
  - 120°: True/False
  - 240°: Essay
- Indicator line on knob: `--brass`, 2px
- Below knob: current value text — 8px, `--text-muted`, `font-mono`
- Drag up/down to cycle through three positions (no intermediate)

##### 3.4.2.4 Options (Multiple Choice Only)

- Only visible when Type = Multiple Choice
- 4 stacked input strips, each:
  - 100% width, 24px height, `--bg-root` bg, 1px `--lab-border`
  - Left: letter indicator (A/B/C/D) — 8px, `--brass`, `font-mono` (10px wide)
  - Right: text input groove (same as question text, but 9px font)
  - Gap between strips: 4px

##### 3.4.2.5 Score Knob

- Knob diameter: 24px
- Range: 0–100
- Default: 10
- Value display: right of knob, "10pts" — 11px, `--text-primary`, `font-mono`

##### 3.4.2.6 Time Limit Knob

- Knob diameter: 24px
- Range: 0–300 seconds
- Default: 60
- Value display: "60s" — 11px, `--text-primary`, `font-mono`
- 0 = no limit

### 3.5 Conditional Branching

#### 3.5.1 Creating a Branch

- **Trigger**: Right-click on any wave node
- **Context menu** (appears at cursor position):
  - 120px × 80px, `--surface` bg, 1px `--lab-border`, chamfer 2px
  - Single option: "Add Branch" — 9px, `--brass`, `font-mono`, centered
  - Hover: bg `#1E1E24`
  - Click: context menu closes, branch creation mode activated

#### 3.5.2 Branch Line

- After activating branch mode: a secondary wave line appears
- **Visual**:
  - Start: originates from the right edge of the source node (same as output jack area)
  - Line: `--brass`, 1px, dashed (`stroke-dasharray: 4 4`)
  - Curves downward/upward (subtle arc) to a target node
- **Target selection**: Click on any other node (cannot target self, cannot target nodes left of source)
  - Target node border flashes `--teal` (200ms) on valid selection
  - Branch line connects source → target

#### 3.5.3 Branch Condition Label

- Positioned at the midpoint of the branch arc
- Text: "Answer = B" — 8px, `--text-muted`, `font-mono`
- **Editable**: Click the label → inline text field appears
  - Default: "Answer = A"
  - Condition syntax freeform: any text up to 20 characters
  - Press Enter to commit, Escape to revert

#### 3.5.4 Branch Constraints

- A node can have multiple outgoing branches (fan-out, unlimited)
- A node can receive multiple incoming branches from different sources
- Branches cannot create cycles (enforced: a branch cannot target a node that is at or before the source node in the main wave sequence)
  - On violation: branch attempt rejected, target node border flashes `--danger` (200ms)
- Branch does not replace the main wave connection — main teal line remains
- Branches are rendered above the main wave line (higher z-order)

#### 3.5.5 Deleting a Branch

- Click the branch line → selects it (`--brass` brightens to `#E0B84C`, stroke-width 1.5px)
- Press Delete key → branch fades (150ms) and is removed
- Or right-click on selected branch → "Delete Branch" — 9px, `--danger`, `font-mono` (single-option context menu)

---

## 4. Statistical Spectrum Analyzer

### 4.1 Page Layout

- Full-width workspace below action rail
- Left column: 48px wide, vertical knob rack
- Center: Spectrogram heatmap (flex: 1)
- Bottom-right: Zoom knob

### 4.2 Spectrogram Heatmap

#### 4.2.1 Grid

| Property | Value |
|---|---|
| Width | 100% of remaining workspace |
| Height | 400px (fixed) |
| Background | `--bg-root` |
| Border | 1px `--lab-border` |

#### 4.2.2 Axes

- **X-axis** (bottom): Time — days/weeks/months depending on Resolution knob
  - Tick marks every N units (auto-calculated): 8px tick, 1px `#1F1F23`
  - Labels below ticks: "Mon 3", "Tue 4", etc. — 7px, `--text-muted`, `font-mono`
- **Y-axis** (left): Skills/Courses/Users depending on Metric Type knob × Department filter
  - Tick marks every row: 8px tick, 1px `#1F1F23`
  - Labels left of ticks: truncated (max 8 characters) — 7px, `--text-muted`, `font-mono`
  - Label width: 60px fixed, overflow ellipsis

#### 4.2.3 Cells

- Each cell: 20px × 20px (default at 1x zoom)
- Cell count: grid auto-calculates to fill available space
  - X: `floor(canvasWidth / cellSize)`
  - Y: `floor((canvasHeight - 24pxAxisLabelHeight) / cellSize)`
- Cell borders: 1px `#1F1F23` (subtle separation, no gap)

#### 4.2.4 Cell Color Mapping

| Activity Level | Color | Hex |
|---|---|---|
| No activity | `--bg-root` | `#0B0B0D` |
| Low (1–25%) | Slight teal | `#1A2A2B` |
| Medium (26–50%) | Stronger teal | `#2D4F50` |
| High (51–75%) | Brass tint | `#7A6B30` |
| Completion (100%) | `--success` | `#6A8A5C` |

- Colors are SOLID. No gradients, no linear interpolation between cells.
- Each cell's color is determined by its data value mapped into one of the 5 discrete bands.

#### 4.2.5 Tooltip on Hover

- Hover any cell → tooltip appears (200ms delay)
- Tooltip: 140px × 48px, `--surface` bg, 1px `--lab-border`, chamfer 2px
- Content: "Course: Algebra\nScore: 72%" (two lines, 8px, `--text-primary` / `--text-muted`, `font-mono`)
- Tooltip follows cursor, offset 12px right and 8px down

#### 4.2.6 Redraw Transition

- When any knob changes: spectrogram redraws with 200ms crossfade
- Old cells fade out (opacity 1→0, 100ms)
- New cells fade in (opacity 0→1, 100ms)
- Axes labels redraw instantly (100ms, no fade)

### 4.3 Spectrum Control Knobs (Left Column)

#### 4.3.1 Knob Rack

- Column: 48px wide, aligned to left edge of spectrogram
- Background: `--bg-root`
- Border-right: 1px `--lab-border`
- Padding-top: 16px

#### 4.3.2 Knob Specs (All 4 Knobs)

| Property | Value |
|---|---|
| Diameter | 32px |
| Background | `#1A1A20` (unselected arc) |
| Indicator | `--brass` (selected arc fills clockwise) |
| Rotation range | 0°–270° (bottom-left = start, bottom-right = end) |
| Interaction | Vertical drag (up = increase, down = decrease) |
| Cursor | `ns-resize` |

- Each knob: 32px × 32px, centered in the 48px column
- Below each knob (4px gap): value label — 10px, `--text-muted`, `font-mono`, centered

#### 4.3.3 Knob Functions

##### Knob 1: Date Range

| Position | Value |
|---|---|
| 0°–67.5° | 7d |
| 67.5°–135° | 30d |
| 135°–202.5° | 90d |
| 202.5°–270° | 1y |

- Default: 30d (second position)
- Visual indicator on knob: small dot at the selected position's boundary

##### Knob 2: Department/Group

- Values: dynamically populated from managed groups in the system
- Default: "All"
- Text truncated to 8 characters in value label
- If no groups exist: label shows "—" in `--text-muted`

##### Knob 3: Metric Type

| Position | Value |
|---|---|
| 0°–67.5° | Activity |
| 67.5°–135° | Scores |
| 135°–202.5° | Completion |
| 202.5°–270° | Time |

- Default: Activity
- Each position maps to a different data column for cell coloring

##### Knob 4: Resolution

| Position | Value |
|---|---|
| 0°–90° | Daily |
| 90°–180° | Weekly |
| 180°–270° | Monthly |

- Default: Weekly
- Changes X-axis tick labels and cell width per time unit

### 4.4 Zoom Control

#### 4.4.1 Position

- Bottom-right of spectrogram area
- 8px from bottom, 8px from right edge

#### 4.4.2 Knob Specs

| Property | Value |
|---|---|
| Diameter | 24px |
| Background | `#1A1A20` |
| Indicator | `--teal` (not brass — distinguishes from control knobs) |
| Rotation range | 0°–270° |

#### 4.4.3 Positions

| Position | Value | Cell Size |
|---|---|---|
| 0°–90° | 1x | 20px × 20px |
| 90°–180° | 2x | 40px × 40px |
| 180°–270° | 4x | 80px × 80px |

- Default: 1x
- At 2x and 4x: fewer cells visible, horizontal scrollbar appears if data exceeds canvas width
- Scrollbar: 6px height, `--lab-border` track, `--brass` thumb
- Label below zoom knob: "1x" — 8px, `--text-muted`, `font-mono`

### 4.5 Spectrogram Empty State

- When no data matches filters: entire canvas shows centered text
- "No signal data" — 14px, `--text-muted`, `font-mono`
- Below: "Adjust filters above" — 9px, `--text-muted`, opacity 0.6
- Cells all `--bg-root`, grid lines remain visible

### 4.6 Spectrogram Loading State

- Canvas shows a "scanning" effect: a single horizontal line (2px, `--teal`, 100px wide) sweeps from top to bottom over 2 seconds, repeating
- Line opacity: 0.3

---

## Cross-Cutting Concerns

### Persistence & State

- Library panel open/closed state: ephemeral (not persisted)
- Path module positions and sizes: persisted via `PUT /admin/paths/{id}` API
- Module connections (cables) with thresholds: persisted via `path_step_connections` table
- Wave node positions and properties: persisted via assessment `questions` JSON field / per-question API
- Spectrogram knobs: ephemeral (session-only, reset on page reload)

### Backend API Contract (for reference)

| Endpoint | Method | Purpose |
|---|---|---|
| `/admin/lab/library` | GET | Fetch all modules grouped by tab |
| `/admin/lab/paths` | GET | List all paths in workspace |
| `/admin/lab/paths` | POST | Create new path module |
| `/admin/lab/paths/{id}` | PUT | Update path (name, modules, connections) |
| `/admin/lab/paths/{id}` | DELETE | Remove path |
| `/admin/lab/connections` | POST | Create cable connection between modules |
| `/admin/lab/connections/{id}` | PUT | Update threshold on connection |
| `/admin/lab/connections/{id}` | DELETE | Remove connection |
| `/admin/lab/tests/{id}/wave` | GET | Fetch wave nodes for test |
| `/admin/lab/tests/{id}/wave` | PUT | Save wave node layout + properties |
| `/admin/lab/analytics/spectrum` | GET | Fetch spectrogram data (query params: date_range, department, metric, resolution) |

### Implementation File Structure

```
src/frontend/src/features/admin-lab/
├── components/
│   ├── LibraryPanel.tsx           # Floating module library
│   ├── LibraryPanelTrigger.tsx    # "Library" button
│   ├── ModuleCard.tsx             # Draggable module card (80×80)
│   ├── PathModule.tsx             # Path container (800px, drop zone)
│   ├── PathModuleHeader.tsx       # Editable path name + controls
│   ├── ContentModule.tsx          # Module card inside path (200×120)
│   ├── Cable.tsx                  # SVG Bézier cable component
│   ├── ThresholdPopup.tsx         # Voltage control popup
│   ├── WaveformEditor.tsx         # Wave shaper canvas (400px)
│   ├── WaveNode.tsx               # 48px circle wave node
│   ├── NodePropertiesPanel.tsx    # Right-side properties (280px)
│   ├── SignalInputStrip.tsx       # Groove-style text input
│   ├── Knob.tsx                   # Reusable knob (24px/32px variants)
│   ├── BranchLine.tsx             # Conditional branch (dashed)
│   ├── Spectrogram.tsx            # Heatmap grid (400px)
│   ├── SpectrumKnobRack.tsx       # Left column 4 knobs
│   ├── ZoomControl.tsx            # Bottom-right zoom knob
│   └── ContextMenu.tsx            # Right-click context menu
├── hooks/
│   ├── useModuleLibrary.ts        # Fetch library modules
│   ├── usePathBuilder.ts          # Path CRUD + connections
│   ├── useWaveEditor.ts           # Wave node state + persistence
│   └── useSpectrogram.ts          # Spectrum data fetching
└── page.tsx                       # /admin/lab route page
```
