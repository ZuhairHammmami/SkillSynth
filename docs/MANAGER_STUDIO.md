# Manager Studio — Modular Analog Dashboard for Team Oversight

> **⚠️ `achievements` reference in LED tooltip (line 321) — achievements feature removed.**

## Design Philosophy

The Manager Studio is a modular, synthesizer-inspired dashboard where managers interact with learners, groups, and paths through physical-analog metaphors: amplifier racks, signal-level VU meters, cable patching, and oscilloscope traces. No tables, no charts, no drop-downs. Every interaction feels like patching a modular synth.

---

## 1. Amplifier Rack (Group/Department Display)

### Module Spec
| Property | Value |
|----------|-------|
| Width | 400px |
| Height | 280px |
| Background | `--surface` (`#16161A`) |
| Border | 1px solid `#2A2A2E` |
| Corner radius | 2px |
| Box decoration | chamfered corners — small diagonal cut at each corner (2px clipped via `clip-path: polygon(2px 0, calc(100% - 2px) 0, 100% 2px, 100% calc(100% - 2px), calc(100% - 2px) 100%, 2px 100%, 0 calc(100% - 2px), 0 2px)`) |

### Header Section (30px tall)
```
┌──────────────────────────────────────────────┐
│ ┌────┐  GROUP NAME              [ 12 ]       │
│ │VU  │  ──────────                           │
│ └────┘                                        │
├──────────────────────────────────────────────┤
│                                                │
```
- **VU meter**: 100px wide, 8px tall horizontal bar, positioned left edge
  - 10 solid-color segments, each 8px × 8px, gap 1.5px between segments
  - Segments fill left-to-right based on group average learner progress
  - Color segments: first 3 = `--teal` (`#3D5A5C`), next 4 = `--success` (`#6A8A5C`), last 3 = `--brass` (`#D4A843`)
  - Empty segments: `#1A1A1A`
  - Hover: brief tooltip showing "Avg Progress: 67%"
- **Channel label**: group name, 14px, `--brass` (`#D4A843`), font-family: `Tajawal`, uppercase tracking 0.5px, positioned left of VU
- **Learner count**: right-aligned, JetBrains Mono, 12px, `--text-muted` (`#8A8882`), padded with brackets: `[ 12 ]`

### Content Area (remaining space)
- Flexbox `row wrap` with 8px gap
- Holds Learner Bank modules
- Scrollable vertically if overflow (custom thin scrollbar: 4px wide, `#2A2A2E` track, `#3D5A5C` thumb)

### States
| State | Visual Change |
|-------|---------------|
| Normal | Standard module |
| Active (any learner has new activity) | Header border-bottom pulses `--teal` (1s cycle, opacity 0.4→0.8) |
| Empty group | Content area shows centered muted text "No learners in this group" (12px, `--text-muted`, italic) |
| Dragging cable over | Entire module border shifts to `--brass`, 1px |

---

## 2. Learner Bank — Signal Level Indicators

### Module Spec (per learner)
| Property | Value |
|----------|-------|
| Width | 120px |
| Height | 80px |
| Background | `--surface` (`#16161A`) |
| Border | 1px solid `#2A2A2E` |
| Corner radius | 2px |
| Position | relative (for LED and jack absolute children) |

### Layout (top-down)
```
┌──────────────────────────┐
│ ● LED      Name Here     │  ← 10px row
│ ┌──────┐ ┌─┐             │
│ │ Name │ │V│  ⊙ output   │  ← 30px row: avatar + VU + jack
│ │  av  │ │U│             │
│ └──────┘ └─┘  ⊙ input   │  ← LED bottom or left
└──────────────────────────┘
```

**Row 1 (top, 18px):**
- **LED**: 6px dot, `border-radius: 50%`, position absolute top-right (4px from edges). See Section 5 for states.
- **Name**: 10px, `--text-primary` (`#F5F0E7`), truncated with ellipsis after 80px. `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`

**Row 2 (center, 40px):**
- **Avatar**: 20px circle (`border-radius: 50%`), border 1px `#2A2A2E`
  - If no image: initials in 9px bold, `--text-muted`, background `#1A1A1A`
- **VU Meter**: vertical bar, 6px wide, 40px tall, positioned next to avatar
  - Background track: `#1A1A1A`
  - Fill: bottom-up, width 100%, `transition: height 200ms ease-out`
  - **Scale marks**: three 1px horizontal lines crossing the full 6px width at 25%, 50%, 75% from bottom. Color `#2A2A2E`. Drawn as `::before` pseudo-elements on the track.
  - Fill colors (based on path progress %):
    - 0-33%: `--danger` tint — `#C8553D` at full opacity
    - 34-66%: `--teal` — `#3D5A5C`
    - 67-100%: `--success` — `#6A8A5C`
  - Animation: on progress update, the fill bar smoothly transitions height over 200ms ease-out. If progress jumps across zones (e.g., 32% → 35%), the color transitions with a 100ms delay to avoid jarring cutover.
- **Output jack**: right side of module, 8px circle (`border-radius: 50%`), background `#2A2A2E`, border 1px `#3D5A5C`. Position absolute, right 4px, center Y. Cursor: pointer.
  - Hover: border becomes `--brass`, inner circle fills to 6px `--brass` dot
  - Active drag: jack glows — box-shadow `0 0 6px rgba(212,168,67,0.5)`
- **Input jack**: left side, 8px circle, background `#2A2A2E`, border 1px `#3D5A5C`. Position absolute, left 4px, center Y.
  - Receives notification pulses (achievement LED pulses here as a brief glow)

**Row 3 (bottom, 12px):**
- Small muted label showing current path short name (e.g., "FPGA · 43%"), 8px, `--text-muted`
- Or empty space if unenrolled

### States
| State | Visual Change |
|-------|---------------|
| Idle | Default styling |
| Active (recent interaction) | Avatar border becomes `--teal` (1px) |
| Selected (for cable drag) | Module border `--brass`, slight scale up `transform: scale(1.02)` |
| Hover | `#2A2A2E` border brightens to `#3D5A5C` |
| Unenrolled | No path label in bottom row; VU bar flat at 0% (empty) |

---

## 3. Connecting Learners to Paths (Cable Patching)

### Interaction Flow

**Step 1 — Initiate Cable Drag**
- Manager clicks (mousedown) on any learner module's output jack (right side, 8px circle)
- A cable line appears from jack center following cursor — a 2px solid `--brass` SVG `<path>` with bezier curve
- The source jack glows: `box-shadow 0 0 8px rgba(212,168,67,0.6)`
- Cursor changes to crosshair

**Step 2 — Drag Over Targets**
- As cable endpoint hovers over a target module's input jack:
  - Target jack border expands: `width: 12px; height: 12px` (from 8px), border-color `--brass`, transition 100ms
  - Target module border briefly shifts to `--brass`
  - If path module: a brief text label appears next to jack showing path title (10px, `--text-primary`)
- If cable endpoint is released over empty space: cable snaps back (200ms ease-in animation returning to source jack) and no connection is made

**Step 3 — Drop to Connect**
- On `mouseup` over a valid path module's input jack:
  - Both modules flash simultaneously: overlay `rgba(212,168,67,0.3)` for 300ms then fade out
  - Cable locks in place with a 2px solid `--brass` SVG bezier path
  - Source jack: becomes `--teal` filled (indicating connected)
  - Target jack: becomes `--brass` filled (indicating active input)
  - Enrollment API call fires (`POST /api/enrollments`). On failure, cable disintegrates (200ms particle burst) and jacks return to default.

**Cable Rendering**
- SVG layer overlay on the workspace (position fixed, full viewport, pointer-events none for non-cable areas)
- Cable path: cubic bezier (`M x1,y1 C cx1,cy1 cx2,cy2 x2,y2`) with control points creating a gentle S-curve
- Color: `--brass` solid, 2px stroke, no fill
- Drop shadow on cable: `filter: drop-shadow(0 0 2px rgba(212,168,67,0.3))`

**Disconnecting**
- Double-click on any cable:
  - Cable stroke becomes `--danger` (`#C8553D`) and width increases to 3px
  - A small X icon (12px × 12px, `--danger`) appears at cable midpoint
  - Clicking the X icon:
    - Cable plays a disintegration animation: 300ms particle burst along the path (12 particles, golden `--brass` fading to `#1A1A1A`, moving perpendicular to the curve)
    - Cable removed from DOM
    - Enrollment API call fires (`DELETE /api/enrollments/{id}`)
  - Clicking anywhere else: cable returns to default `--brass` 2px

**Multi-Learner Bundling**
- When 2+ learners are patched to the same path, cables visually bundle:
  - Primary cable (thickest): 3px `--brass` from path input jack → first 20% of distance
  - Branch cables (thinner): 1.5px `--teal` splitting off to each learner's output jack
  - The SVG path uses a shared trunk near the path module that fans out toward learners
  - A small number badge (8px, `--brass` text on `#1A1A1A` background, `border-radius: 2px`) at the trunk split showing cable count (e.g., "4")

---

## 4. Activity Oscilloscope (Learner Detail View)

### Trigger
- Double-click on any Learner Bank module → expands into oscilloscope view
- Transition: 200ms ease-out, module scales from 120px×80px to 600px×350px, positioned relative to original location (or centered if near edge)

### Expanded Module Spec
| Property | Value |
|----------|-------|
| Width | 600px |
| Height | 350px |
| Background | `--surface` (`#16161A`) |
| Border | 1px solid `#2A2A2E` |
| Corner radius | 2px |
| z-index | 100 (above all other modules) |
| Position | fixed, centered in viewport (or offset to keep within bounds) |
| Chamfer | Same clip-path as amplifier modules |

### Layout
```
┌──────────────────────────────────────────────────────┐
│ Learner Name · Path: FPGA Design       ✕             │  ← 24px header
├──────────────────────────────────────────────────────┤
│                                                        │
│   ┌──────────────────────────────────────────┐        │
│   │ ╷                                          │        │
│   │100┤    ╱╲              ╱╲                  │        │
│   │   │   ╱  ╲    ╱╲     ╱  ╲                 │        │
│   │75 ├──╱────╲──╱──╲──╱────╲──╱╲──           │        │  ← 240px scope
│   │   │ ╱      ╲╱    ╲╱      ╲╱  ╲            │        │
│   │50 ├─╱───────────────╲──────╲───╲           │        │
│   │   │╱                  ╲      ╲  ╲          │        │
│   │25 ├────────────────────╲──────╲──╲         │        │
│   │   │                     ╲      ╲  ╲        │        │
│   │ 0 ┼──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──    │        │
│   │   │ 7│14│21│28│  │  │  │  │  │  │  │       │        │
│   └──────────────────────────────────────────┘        │
│                                                        │
│   ⊙ Time Range    ⊙ Refresh    ⊙ Export               │  ← 40px controls
└──────────────────────────────────────────────────────┘
```

### Header Bar
- Learner full name: 14px, `--brass`, Tajawal medium
- Current path name: 12px, `--text-muted`, preceded by "·"
- Close button (✕): absolute top-right, 16px × 16px, `--text-muted`, hover becomes `--danger`

### Time-Domain Scope Display
- Grid area: 500px × 220px, positioned center of expanded module
- **X-axis** (horizontal, bottom): time labels in JetBrains Mono, 9px, `--text-muted`
  - Default: last 30 days. Tick marks at 7-day intervals (Day 0, Day 7, Day 14, Day 21, Day 28)
  - Each tick is a faint vertical line: 1px, `#1F1F23`, extending full height of grid
  - Label below each tick: "7", "14", "21", "28" (numeric day)
- **Y-axis** (vertical, left): activity labels in JetBrains Mono, 9px, `--text-muted`
  - Tick marks at 25%, 50%, 75%, 100% — each is a horizontal line: 1px, `#1F1F23`, extending full width of grid
  - Labels left of ticks: "25", "50", "75", "100"
- **Trace line**: `--brass` (`#D4A843`), 2px stroke, `stroke-linejoin: round`, `stroke-linecap: round`, no fill
  - Data points: one per day (activity composite score: weighted average of hours + test scores)
  - On open: line draws left-to-right over 500ms using CSS `stroke-dasharray` + `stroke-dashoffset` animation
- **Crosshair on hover**: vertical ruler line follows cursor X position (1px, `--brass`, dashed), horizontal ruler line follows cursor Y. At intersection, a small circle (4px, `--brass` fill) marks the exact data point.
  - **Tooltip**: appears 12px above the crosshair circle
    - Background: `#0B0B0D`, border 1px `#2A2A2E`, padding 4px 8px, font 9px JetBrains Mono
    - Content: `"Day 14 · 3.2h · Test: 85%"` (date, hours spent, avg test score)
    - Arrow pointing down at crosshair
- **Scroll wheel**: changes visible time range
  - Scroll up (from default 30 days): zooms to 7-day granularity (each tick = 1 day, labels every day)
  - Scroll down: zooms out to 90-day view (tick labels every 14 days)
  - Cycle: 7d → 30d → 90d → 7d (wraps)
  - Transition: 150ms ease-out on grid/tick redraw
- **Empty state** (no activity data): center text "No activity data" (12px, `--text-muted`, italic), a flat horizontal line at Y=0 in `--brass` at 0.3 opacity

### Controls Below Scope
Three knobs in a row, 24px each, centered horizontally, 8px apart.

**Knob spec** (shared across all three):
- Outer circle: 24px diameter, background `#1A1A1A`, border 1px `#2A2A2E`, `border-radius: 50%`
- Inner indicator: a 2px wide × 6px tall line from center toward top, `--brass`
- Rotation: `transform: rotate(Xdeg)`, transition 100ms
- Cursor: pointer

**Knob 1 — Time Range**
- Rotation maps to range: -45° = 7d, 0° = 30d (default), 45° = 90d
- Click/drag rotates knob, scope updates live
- Equivalent to scroll wheel (alternative UX)

**Knob 2 — Refresh**
- Single-click: knob spins 360° over 300ms, then recenters
- Refetches learner activity data from API (`GET /api/analytics/learner/{id}/activity`)
- On refetch: scope trace fades out (100ms), new trace draws in (500ms)

**Knob 3 — Export**
- Single-click: knob rotates to 90° (pointing right) and locks for 400ms
- Generates a static "wave snapshot" — a PNG rendering of the current scope (canvas-based)
- Downloads as `learner_{id}_oscilloscope_[date].png`
- After download: knob springs back to 0° (200ms ease-out)
- If export fails: knob rattles (quick oscillation ±15°, 3 cycles, 200ms)

### Close Behavior
- Clicking ✕ or pressing Escape:
  - Module collapses to original mini Learner Bank module position
  - Transition: 150ms ease-in (scale from 600px→120px width)
  - If cable was present, it reconnects visually (brief flash on both jacks)

---

## 5. Manager Notifications — LED System

### LED Spec
| Property | Value |
|----------|-------|
| Size | 6px diameter circle |
| Radius | `border-radius: 50%` |
| Position | absolute, top 4px, right 4px on Learner Bank module |
| z-index | 10 |

### States & Animations

| State | Color | Animation | Opacity | Meaning |
|-------|-------|-----------|---------|---------|
| Off | `#1A1A1A` | None, static | 1.0 | Module idle, no activity in 7+ days |
| Normal | `--teal` (`#3D5A5C`) | Slow pulse, 2s cycle | 0.3 → 0.8 | Learner active in assigned paths |
| Achievement | `--brass` (`#D4A843`) | Fast pulse, 0.5s cycle | 0.5 → 1.0 | New certificate, high score, or milestone |
| Urgent | `--danger` (`#C8553D`) | 3 quick blinks (150ms on, 100ms off, repeat 3×), then 3s pause | 0.6 (on), 0.1 (off) | Failed test, falling behind (>20% below avg), or 5+ days inactive after enrollment |

**CSS keyframes for pulses:**
```css
@keyframes led-normal {
  0%, 100% { opacity: 0.3; }
  50%      { opacity: 0.8; }
}

@keyframes led-achievement {
  0%, 100% { opacity: 0.5; }
  50%      { opacity: 1.0; }
}

@keyframes led-urgent {
  0%, 49%  { opacity: 0.6; }
  50%, 99% { opacity: 0.1; }
  /* 3 repetitions via animation-iteration-count: 3 */
}
```

### LED Tooltip
- Hovering on any LED shows tooltip after 400ms delay
- Tooltip: 140px wide, background `#0B0B0D`, border 1px `#2A2A2E`, padding 6px
- Content varies by state:
  - Off: "No activity since March 12"
  - Normal: "Active in FPGA Design · Last: 2h ago"
  - Achievement: "Completed Module 4 · Score 92%"
  - Urgent: "⚠ Behind schedule · Avg dropped 15%"

### Multi-LED Grouping
- When a group (Amplifier Rack module) has many learners with urgent states, the group's overall header gets a summary LED: a 10px dot (larger than individual) in the right corner of the header
  - If any learner is urgent: `--danger` slow pulse (1s cycle)
  - If any learner has achievement but no urgent: `--brass` slow pulse
  - Otherwise: `--teal` static
- Hover tooltip: "3 urgent, 2 achievements"

---

## 6. Overall Manager Workspace Layout

### Top Rail
- Full width, 40px tall, background `--surface`, bottom border 1px `#2A2A2E`
- Content:
  - Left: "MANAGER STUDIO" label, 14px, `--brass`, uppercase, letter-spacing 2px, Tajawal
  - Or: a manager section selection knob (24px knob, rotate to select between "Studio", "Reports", "Settings") — if knob approach, current selection shown as text to the right of knob

### Workspace (scrollable area below rail)
- Background: `--bg-root` (`#0B0B0D`)
- Padding: 24px horizontal, 16px vertical
- Layout: flexbox column, gap 24px

### Left Sidebar — Floating Mini Legend
- Position: fixed left, 16px from left edge, 100px from top
- Module: 120px wide, background `--surface`, border 1px `#2A2A2E`, padding 8px
- No chamfer on this module (or apply same chamfer)
- Content:
  - Title: "LED" (9px, `--text-muted`, uppercase, tracking 1px)
  - 4 rows, each 16px tall:
    - 6px dot + label (8px, `--text-muted`): "● idle", "● active", "★ achievement", "● urgent"
    - Colors match LED states (Off = `#1A1A1A`, Normal = `--teal`, Achievement = `--brass`, Urgent = `--danger`)
  - Legend rows have no pulse animation (static color swatches)
- Collapsible: small X at top-right hides legend; reappears via small "?" icon at same position

### Right Side — Add Group Handle
- Fixed right, 16px from right edge, vertically centered (top 50%)
- A tall thin module: 32px wide, 120px tall, background `--surface`, border 1px `#2A2A2E`
- Rotated text: "+ Add Group" vertical text, 9px, `--brass`, writing-mode vertical-rl, letter-spacing 1px
- Hover: background `#1A1A1A`, border `--brass`
- Click: opens inline editor at bottom of workspace (not a modal) — text input for "Group Name" (14px, 200px wide, background `#1A1A1A`, border 1px `#2A2A2E`), "Create" button (brass 1px border, brass text). On submit: new Amplifier Rack module appended with fade-in (150ms).

### Amplifier Rack Stacking
- Amplifier Rack modules stack vertically with 24px gap
- Drag handle on top-left of each module (8px × 16px pill, `#2A2A2E`, cursor grab) — reorder within workspace via drag-and-drop (swap animation 150ms)
- If more than 4 racks: workspace becomes vertically scrollable (thin 4px scrollbar `#2A2A2E` track, `#3D5A5C` thumb)

### Initial Empty State
- If no groups exist: centered message in workspace
  - 100px tall module: background `--surface`, border 1px `#2A2A2E`
  - Text: "No groups yet. Add one to get started." (14px, `--text-muted`)
  - "+ Add Group" button (brass text, border 1px `--brass`, padding 8px 16px)

### Responsive Behavior
- Minimum workspace width: 840px (accommodates 2 amplifier racks side-by-side if manager chooses to arrange as grid instead of stack — via a toggle knob at top rail)
  - Grid toggle: 20px knob at top rail, rotates 90° between "stack" (vertical, default) and "grid" (2 columns)
- Below 840px: forces vertical stack layout, hides legend (moves to collapsible icon)

---

## Appendix A: API Endpoints (Backend)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/manager/groups` | List all groups with learner summaries |
| `POST` | `/api/manager/groups` | Create new group |
| `DELETE` | `/api/manager/groups/{id}` | Remove group |
| `PATCH` | `/api/manager/groups/{id}` | Update group name |
| `POST` | `/api/enrollments` | Enroll learner in path (cable connect) |
| `DELETE` | `/api/enrollments/{id}` | Remove enrollment (cable disconnect) |
| `GET` | `/api/analytics/learner/{id}/activity` | Activity oscilloscope data (30d/7d/90d) |
| `GET` | `/api/analytics/learner/{id}/progress` | Current progress % for VU meter |
| `GET` | `/api/notifications/manager` | LED state updates (SSE stream) |

## Appendix B: Component Tree (Frontend)

```
ManagerStudioPage
├── TopRail
│   ├── SectionKnob (optional)
│   └── ViewToggleKnob (stack/grid)
├── Workspace
│   ├── AmplifierRack (×N)
│   │   ├── VUMeter (horizontal, group-level)
│   │   ├── LearnerBank (×M)
│   │   │   ├── LED (notification dot)
│   │   │   ├── VUMeter (vertical, individual)
│   │   │   ├── AvatarCircle
│   │   │   ├── OutputJack (drag source)
│   │   │   └── InputJack (drop target)
│   │   └── Learners → grid layout
│   ├── AddGroupHandle
│   └── EmptyState (when no groups)
├── CableLayer (SVG overlay)
│   └── CablePath (×P)
├── OscilloscopeModal (expanded learner)
│   ├── ScopeCanvas
│   ├── CrosshairOverlay
│   └── ControlKnobs (TimeRange, Refresh, Export)
├── FloatingLegend
└── SSEConnection (LED state stream)
```

## Appendix C: Color Tokens Reference

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-root` | `#0B0B0D` | Workspace background |
| `--surface` | `#16161A` | All module backgrounds |
| `--brass` | `#D4A843` | Active cables, VU active segments, headers, achievement LED |
| `--teal` | `#3D5A5C` | Normal LED, VU mid segments, connected jack |
| `--text-primary` | `#F5F0E7` | Names, primary labels |
| `--text-muted` | `#8A8882` | Secondary labels, axis ticks, legends |
| `--success` | `#6A8A5C` | VU high segments (67-100%) |
| `--danger` | `#C8553D` | Urgent LED, disconnect icon, VU low fill |
| `#1A1A1A` | `#1A1A1A` | Inactive elements, VU track background |
| `#2A2A2E` | `#2A2A2E` | Module borders, grid lines, scale marks |
| `#1F1F23` | `#1F1F23` | Oscilloscope grid lines |
