# Learner Experience — Signal Path Workspace

*Design token reference: AGENTS.md §Mandatory Tokens (--bg-root, --surface, --brass, --teal, --text-primary, --text-muted, --success, --danger, 8px grid, 1px #2A2A2E borders, chamfer modules, 50% knob radius).*

---

## 1. Signal Path Module — The Learner's Learning Path

A horizontal row of physically-connected modules spanning the workspace width. Each module represents one stage in the learner's path. The row uses flexbox with `gap: 8px`, centered within the workspace container, with horizontal overflow scroll (`overflow-x: auto`, `scrollbar-width: thin`).

### 1.1 Module Dimensions & Structure

| Property | Value |
|----------|-------|
| Width | 260px (collapsed), 600px (expanded) |
| Height | 180px (collapsed), min 400px (expanded, content-dependent) |
| Background | `--surface` (`#16161A`) |
| Border | 1px solid `#2A2A2E` |
| Border-radius | 2px (chamfered — use `clip-path: polygon(2px 0, calc(100% - 2px) 0, 100% 2px, 100% calc(100% - 2px), calc(100% - 2px) 100%, 2px 100%, 0 calc(100% - 2px), 0 2px)`) |
| Padding | 12px |
| Font family | `var(--font-tajawal)` |
| Position | relative (for jack absolute positioning) |

#### 1.1.1 Header Strip
- 4px tall colored bar spanning full module width at top
- Positioned `absolute`, `top: 0`, `left: 0`, `right: 0`
- Z-index above module border

#### 1.1.2 Jacks (Input / Output)
- **Input jack**: 10px diameter circle, `position: absolute`, `left: -5px`, `top: 50%` (`transform: translateY(-50%)`)
  - Inner ring: 6px diameter, recessed via `box-shadow: inset 0 1px 2px rgba(0,0,0,0.6)`
  - Fill: `#1A1A1E`, border: 1px solid `#2A2A2E`
- **Output jack**: 10px diameter circle, `position: absolute`, `right: -5px`, `top: 50%` (`transform: translateY(-50%)`)
  - Same visual as input jack
- Jack "activated" state (when module is active): inner ring fill `--brass`

#### 1.1.3 Content Area (Collapsed)
- **Genre icon**: 28px × 28px, positioned `top: 16px`, `left: 12px`
  - SVG from icon set (synth-waveform, filter, envelope, sequencer, etc.)
- **Title**: 14px, `font-weight: 500` (medium), `color: --text-primary`, `margin-top: 8px`
  - Truncated to 1 line with `text-overflow: ellipsis`
- **Horizontal wave indicator**: 12px height, full content width, `margin-top: auto` (pushed to bottom of module), `position: absolute`, `bottom: 12px`
  - SVG waveform line spanning width
  - Implemented as inline SVG `<path>` with computed `d` attribute

### 1.2 Module States

#### 1.2.1 Locked (`state: "locked"`)
| Visual | Value |
|--------|-------|
| Border | `1px dashed #2A2A2E` |
| Header strip | `background: #2A2A2E` |
| Genre icon | `opacity: 0.35` |
| Wave indicator | Flat horizontal line at y=50%, `stroke: #2A2A2E` |
| Title color | `--text-muted` |
| Jacks | Default recessed (idle) |
| Cursor | `not-allowed` |
| Click | No expand (no-op) |

SVG wave `d` for locked: `"M 0,6 L {{width}},6"` (straight line).

#### 1.2.2 Available / Upcoming (`state: "available"`)
| Visual | Value |
|--------|-------|
| Border | `1px solid #2A2A2E` |
| Header strip | `background: --text-muted` (`#8A8882`) |
| Genre icon | `opacity: 1.0` |
| Wave indicator | Flat line at y=50%, `stroke: --text-muted` |
| Title color | `--text-primary` |
| Jacks | Default recessed (idle) |
| Cursor | `pointer` |
| Click | Expands module |

#### 1.2.3 Active (`state: "active"`)
| Visual | Value |
|--------|-------|
| Border | `2px solid --brass` (`#D4A843`) |
| Header strip | `background: --brass` |
| Genre icon | `opacity: 1.0`, `filter: drop-shadow(0 0 2px rgba(212, 168, 67, 0.3))` — brass tint |
| Wave indicator | Low-frequency oscillation: gentle sine wave, amplitude 3px, period ~60px |
| Jacks | Input/output inner ring fill: `--brass` |
| Cursor | `pointer` |
| Title color | `--text-primary` |

SVG wave `d` for active: `"M 0,6 Q {{x1}},{{y1}} {{x2}},{{y2}} ..."` — computed sine with `A = 3px`, `λ = 60px`.

Animation: wave oscillates continuously via CSS `@keyframes wavePulse`:
```css
@keyframes waveActive {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-1px); }
}
```
Applied to SVG `path` with `animation: waveActive 3s ease-in-out infinite`.

#### 1.2.4 Completed (`state: "completed"`)
| Visual | Value |
|--------|-------|
| Border | `1px solid --success` (`#6A8A5C`) |
| Header strip | `background: --success` |
| Genre icon | `opacity: 1.0`, with checkmark overlay (12px × 12px `--success` check icon, `position: absolute`, `top: 12px`, `right: 12px`) |
| Wave indicator | Steady sine wave at 100% amplitude (6px), `stroke: --success` |
| Title color | `--text-primary` |
| Jacks | Inner ring fill: `--success` |
| Cursor | `pointer` (can re-open) |

SVG wave `d` for completed: smooth sine, `A = 6px`, `λ = 40px`, full wave visible.

### 1.3 Cable Connections

Cables are rendered as absolutely-positioned SVG `<svg>` elements spanning from output jack of module N to input jack of module N+1.

#### 1.3.1 Cable SVG Container
- `position: absolute`, `top: 0`, `left: 0`, `width: 100%`, `height: 100%`
- `pointer-events: none`, `z-index: 1`
- Each cable is a `<path>` with `fill="none"`, `stroke-linecap="round"`

#### 1.3.2 Bézier Curve Parameters
- Start point: output jack center of module N (`right edge + 5px`, `vertical center`)
- End point: input jack center of module N+1 (`left edge - 5px`, `vertical center`)
- Control point 1: start point + 40px horizontally
- Control point 2: end point - 40px horizontally
- Path: `"M {{startX}},{{startY}} C {{cp1X}},{{cp1Y}} {{cp2X}},{{cp2Y}} {{endX}},{{endY}}"`

#### 1.3.3 Cable States

| State | Stroke | Width | Style |
|-------|--------|-------|-------|
| Completed | `--success` | 2px | Solid |
| Active (current) | `--brass` | 2px | Solid, with opacity animation |
| Upcoming | `--text-muted` | 1px | Dashed (`stroke-dasharray: 4 4`) |

**Active cable pulse animation:**
```css
@keyframes cablePulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}
```
Applied with `animation: cablePulse 2s ease-in-out infinite`.

### 1.4 Inline Expand Behavior

#### 1.4.1 Expand Trigger
- Click on any module with `state !== "locked"`
- `onClick` handler reads `transformOrigin` as center of module rect

#### 1.4.2 Expand Animation (300ms ease-out)
```css
transition: width 300ms ease-out, height 300ms ease-out;
```
- Width: `260px` → `600px`
- Height: `180px` → `min(400px, fit-content)`
- Origin: center of module (`transform-origin: center center`)
- Uses `clip-path: inset(0)` → `clip-path: none` for non-geometric expansion feel
- Neighboring modules: shift right via flexbox gap recalculation; if viewport insufficient, remaining modules wrap to next row (`flex-wrap: wrap`)

#### 1.4.3 Expanded Layout (600px wide, min 400px tall)

```
┌────────────────────────────────────────────────────────────────────┐
│ [header strip: 4px, full width]                                    │
│ [genre icon 28px]  [title 14px]            [state badge]  [X]     │
│ ─────────────────────────────────────────────────────────────────  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  Video Embed Placeholder (16:9, 320×180)                  │     │
│  │  border: 1px solid #2A2A2E, border-radius: 2px           │     │
│  │  chamfered corners via clip-path                          │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                    │
│  Content description text (14px, --text-primary, max 3 lines)     │
│                                                                    │
│  Exercise list:                                                    │
│  ┌── [1] Identify the cutoff frequency ──── ○ ─────────────────┐  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌── [2] Calculate the resonance Q ──────── ○ ─────────────────┐  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│           ┌──────────────────────────────────────┐                │
│           │    [─── Finish Knob 40px ───]        │                │
│           │    "Complete Module"                  │                │
│           └──────────────────────────────────────┘                │
└────────────────────────────────────────────────────────────────────┘
```

**Elements:**
- **Header bar**: condensed — genre icon (20px), title (12px, single line), state indicator (colored dot, 8px)
- **Close icon (X)**: `position: absolute`, `top: 12px`, `right: 12px`, 16px × 16px, `color: --text-muted`, `cursor: pointer`, `hover: color --text-primary`
- **Video embed placeholder**: 320px × 180px (16:9), `border: 1px solid #2A2A2E`, `border-radius: 2px`, chamfered `clip-path`, centered
- **Content text**: 14px, `--text-primary`, `max-height: 3em`, `overflow: hidden`
- **Exercise list items**: `padding: 4px 0`, 13px, `--text-primary`, with radio dots (○) — `border: 1px solid --text-muted`, 10px diameter, `border-radius: 50%`
- **Finish knob**: 40px diameter, `border-radius: 50%`, `border: 2px solid --brass`, `background: --surface`, `position: absolute`, `bottom: 16px`, `right: 16px`
  - Knob marker: vertical line, `width: 2px`, `height: 12px`, `background: --brass`, centered at top
  - On click: `transform: rotate(135deg)` (turning from 0° to 135°), `transition: transform 400ms ease-out`
  - After rotation: module state changes to `"completed"`, wave indicator transitions to steady sine

#### 1.4.4 Collapse (300ms ease-in)
- Click X icon or click module header area
- `transition: width 300ms ease-in, height 300ms ease-in`
- Width: `600px` → `260px`, Height: `400px` → `180px`
- `clip-path: none` → `clip-path: inset(0)` — reverse of expand
- Neighboring modules shift back

---

## 2. Overall Progress Indicator

Full-width waveform trace below the signal path row.

### 2.1 Container
- `width: 100%` (workspace width, minus 16px padding left/right)
- `height: 12px`
- `background: #1F1F23`
- `border: 1px solid #2A2A2E`
- `border-radius: 2px`, chamfered via `clip-path`
- `position: relative`, `overflow: hidden`

### 2.2 Waveform SVG
- `position: absolute`, `inset: 0`
- `width: 100%`, `height: 100%`
- `<path>` spanning full width, `fill: none`, `stroke-width: 1.5px`, `stroke-linecap: round`

#### 2.2.1 Wave Computation
- X-axis: 0 to containerWidth, mapped to completion %, left-to-right
- Amplitude: `A = 4px` (oscillates around vertical center at 6px)
- Frequency: `λ = 20px` per oscillation
- For uncompleted portion (beyond progress): flat line at y=6px
- Completed portion: sine wave with `A = 4px`

### 2.3 Color Gradient
- `0%` to `50%` completion: wave `stroke: --teal` (`#3D5A5C`)
- `50%` to `100%` completion: wave `stroke` interpolates `--teal` → `--brass`
  - Implementation: two `<path>` segments or SVG `<linearGradient>` with two stops
  - Stop 1: `offset="0%"`, `stop-color="--teal"`
  - Stop 2: `offset="100%"`, `stop-color="--brass"`
- `100%` completion: entire wave transitions to `--success` (`#6A8A5C`)

### 2.4 Breathing Animation (at rest)
```css
@keyframes waveBreathe {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.85); }
}
```
- Applied to SVG `<g>` wrapper
- `animation: waveBreathe 4s ease-in-out infinite`
- Only active when no other wave animation is playing

### 2.5 Completion Celebration
- When progress reaches 100%:
  - Wave color transitions to `--success` over 600ms
  - Brief celebratory pulse: `transform: scaleY(1.3)` → back to `scaleY(1)`, 300ms total
  - Three rapid pulses (`animation: celebratePulse 0.3s ease-in-out 3`)
  - After celebration, breathing resumes

---

## 3. Test Interface — The Oscillator

Triggered when a learner selects a test/quiz from a path module's expanded view. Renders as a modal overlay within the workspace (no page navigation).

### 3.1 Oscillator Container
- `position: fixed`, `inset: 0` (full-screen overlay within workspace)
- `background: rgba(11, 11, 13, 0.85)` (semi-transparent `--bg-root`)
- `z-index: 50`
- `display: flex`, `align-items: center`, `justify-content: center`
- `backdrop-filter: blur(2px)`

#### 3.1.1 Central Module
- `width: 80%` of workspace (max 960px)
- `height: 500px`
- `background: --surface` (`#16161A`)
- `border: 1px solid #2A2A2E`, `border-radius: 2px`, chamfered `clip-path`
- `position: relative`, `padding: 24px`
- `display: flex`, `flex-direction: column`, `align-items: center`

### 3.2 Header Area

```
┌──────────────────────────────────────────────────────────────┐
│  Test Name (14px, brass)              [Spiral Timer 40px]   │
│  ─────────────────────────────────────────────────────────── │
│                                                              │
│                    [Waveform Display]                        │
│                                                              │
│                    [Answer Knobs A B C D]                   │
│                                                              │
│                       [Patch Answer]                         │
│                    Question 3/10                             │
└──────────────────────────────────────────────────────────────┘
```

#### 3.2.1 Test Name Label
- `position: absolute`, `top: 16px`, `left: 20px`
- `font-size: 14px`, `color: --brass`, `font-weight: 500`

#### 3.2.2 Spiral Timer
- `position: absolute`, `top: 12px`, `right: 20px`
- `width: 40px`, `height: 40px`
- Implemented as SVG `<path>` with spiral curve
- Spiral parameters (polar):
  - Start: center (20, 20), `r = 0`
  - End: outer edge, `r = 18`
  - Number of turns: 2.5 (full rotations)
  - `d` attribute computed as: `M 20,20` then cubic beziers for each turn
- **Unwinding animation**: as `timeRemaining / totalTime` decreases from 1 to 0, the spiral path's visible length shrinks from outside in
  - SVG `stroke-dasharray` + `stroke-dashoffset` technique
  - `totalLength` ≈ 283px (circumference of 2.5-turn spiral, r=18)
  - `stroke-dashoffset` transitions from 0 to `totalLength` over test duration
  - `transition: stroke-dashoffset 1s linear` (continuous smooth unwind)
- **Color**: `stroke: --brass` normally; when `timeRemaining / totalTime < 0.25`, `stroke: --danger`
  - Pulse animation at <25%: `@keyframes timerUrgency { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }` at 1s cycle
- **At 0**: spiral disappears (`stroke-dashoffset = totalLength`), test auto-submits current answers
- `fill: none`, `stroke-width: 2px`

### 3.3 Waveform Question Display

#### 3.3.1 Waveform Canvas
- Central area: `width: 70%` of oscillator module, `height: 160px`
- SVG or Canvas element
- `margin: 48px 0 24px 0`
- `background: transparent`

#### 3.3.2 Question Text
- Rendered above waveform: `font-size: 16px`, `color: --text-primary`, `max-width: 80%`
- `max-height: 2.8em` (2 lines), `overflow: hidden`, `text-overflow: ellipsis`
- `text-align: center`
- `margin-bottom: 8px`

#### 3.3.3 Rest Wave (no question interaction)
- Gentle sine pattern: `A = 8px`, `λ = 30px`
- `stroke: --text-muted`, `opacity: 0.5`
- `@keyframes waveIdle { 0%,100% { d: ... } 50% { d: ... } }` — subtle phase shift (2s)

#### 3.3.4 Question Appears
- Wave briefly spikes: amplitude jumps to `A = 20px` for 200ms, then settles to `A = 10px`, `λ = 24px`
- `stroke: --brass` (temporary)
- Duration: 400ms spike → 300ms settle

### 3.4 Answer Selection — Four Knobs

```
         [A]           [B]           [C]           [D]
    Answer Text   Answer Text   Answer Text   Answer Text
```

#### 3.4.1 Knob Specifications
- Each knob: 32px diameter circle
- `border-radius: 50%` (50% radius on knobs only — per design token)
- `border: 2px solid #2A2A2E`
- `background: --surface`
- `position: relative`
- `cursor: pointer`
- Knob marker: 2px wide, 8px tall line, `background: --text-muted`, centered at top of knob
  - `position: absolute`, `top: 2px`, `left: 50%`, `transform: translateX(-50%)`

#### 3.4.2 Answer Labels
- Below each knob: `font-size: 12px`, `color: --text-primary`, `text-align: center`
- `max-width: 80px`, `overflow: hidden`, `text-overflow: ellipsis`
- `margin-top: 6px`

#### 3.4.3 Selection Behavior
- On click: knob rotates `transform: rotate(45deg)`, `transition: transform 200ms ease-out`
- Marker color changes to `--brass`, border changes to `2px solid --brass`
- Previous selection: rotates back to 0°, border resets to `#2A2A2E`
- Only one knob active at a time (radio behavior enforced via state)
- `box-shadow: none` (no glow allowed)

### 3.5 Submit — "Patch Answer"

- Button centered below knobs, `margin-top: 16px`
- `font-size: 13px`, `color: --brass`, `font-weight: 500`
- No background, no border, no padding on container — text-only
- `cursor: pointer`
- Hover: `text-decoration: underline` with `text-decoration-color: --brass`
- Active: `opacity: 0.7`
- Only enabled when one knob is selected

### 3.6 Answer Feedback — Wave Reactions

#### 3.6.1 Correct Answer
- Wave transitions: `A = 8px`, stable smooth sine, `stroke: --success`
- Brief 300ms upward sweep: wave translates `-6px` then returns to center
  - `@keyframes correctSweep { 0% { transform: translateY(0); } 50% { transform: translateY(-6px); } 100% { transform: translateY(0); } }`
- All cables within the oscillator module pulse once: `opacity` 0.5 → 1 → 0.5, 300ms
- Selected knob: brief `transform: rotate(90deg)` (full quarter turn confirmation), then settles to 45°

#### 3.6.2 Wrong Answer
- Wave distorts violently: jagged edges via randomized SVG points
  - Computed `d` attribute: every 8px along X, Y randomly offsets ±6px from base sine
  - `stroke: --danger`
  - Duration: 400ms, then resets to rest sine
  - `@keyframes wrongDistort { 0% { d: ...sine... } 25% { d: ...jagged... } 50% { d: ...jagged2... } 75% { d: ...jagged3... } 100% { d: ...sine... } }`
- Wrong knob jiggles: `@keyframes jiggle { 0%,100% { transform: rotate(45deg); } 25% { transform: rotate(50deg); } 75% { transform: rotate(40deg); } }`
  - 5° oscillation around current rotation, 200ms, 3 cycles

#### 3.6.3 Timeout
- Wave flattens to straight horizontal line at vertical center
- `transition: d 500ms ease-out` (sine → flat)
- Text appears below waveform: `"Signal Lost"` in `--danger`, 14px, uppercase, letter-spacing 2px
- Test is locked — no further interaction allowed
- After 2s, oscillator closes and returns to path

### 3.7 Question Transition
- After correct answer: 200ms pause
- Wave sweeps down (translateY(+8px)) and up (translateY(-2px)) → back to center
  - `@keyframes wipeTransition { 0% { transform: translateY(0); } 30% { transform: translateY(8px); opacity: 0; } 60% { transform: translateY(-2px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }`
- Duration: 500ms total
- New question content fades in during last 200ms of transition
- Oscillator screen updates: question text, wave pattern resets to rest sine

### 3.8 Progress Counter
- `position: absolute`, `bottom: 20px`, `center` (`left: 50%`, `transform: translateX(-50%)`)
- `font-size: 12px`, `color: --text-muted`
- Format: `"Question 3/10"`

### 3.9 Test Completion

#### 3.9.1 Final Answer Submitted
- Wave rises: `A` increases from 8px to 24px over 600ms (`transition: d 600ms ease-out`)
  - Single large peak at center: `d` path calculated with one large oscillation
  - Peak holds for 300ms, then settles to smooth steady sine at `A = 8px`
- Wave color: `--success`
- All cables in the oscillator pulse synchronously: `opacity` 0.5 → 1 → 0.5, 500ms

#### 3.9.2 Score Display
- Appears below waveform after wave settles (300ms delay)
- `font-size: 20px`, `color: --brass`, `font-weight: 700`
- Format: `"Frequency: 8/10 · 80%"`
- `font-variant-numeric: tabular-nums` for stable kerning

#### 3.9.3 Return to Path Button
- Below score: `margin-top: 12px`
- `font-size: 13px`, `color: --brass`, `cursor: pointer`
- Text: `"Return to Path"`
- Hover: `text-decoration: underline`
- Click: oscillator overlay fades out (`opacity: 1 → 0`, 200ms ease), path module view is restored

---

## 4. Path Completion Celebration

Triggered when all modules in a learning path are set to `state: "completed"`.

### 4.1 Cable Celebration
- All cable SVG paths in the path row pulse simultaneously
- `animation: pathCelebrate 0.5s ease-in-out 3` (3 pulses)
```css
@keyframes pathCelebrate {
  0%, 100% { opacity: 0.7; stroke: --brass; }
  50% { opacity: 1; stroke: --success; }
}
```

### 4.2 Progress Wave Finalization
- The overall progress indicator wave reaches 100%
- Color transitions to `--success` (`transition: stroke 600ms ease`)
- Celebratory pulse: `transform: scaleY(1.3)` → `scaleY(1)`, 3 rapid cycles (300ms each)
- After celebration: wave holds steady at `--success`, breathing animation disabled

### 4.3 "Path Patched" Badge
- Appears to the right of the progress wave container (or at end of path row)
- `display: inline-flex`, `align-items: center`, `gap: 6px`
- `border: 1px solid --success`, `border-radius: 2px` (chamfered)
- `padding: 2px 10px`
- `font-size: 12px`, `color: --success`, `font-weight: 500`
- Text: `"Path Patched"`
- Entrance animation: `@keyframes badgeIn { 0% { opacity: 0; transform: scale(0.9); } 100% { opacity: 1; transform: scale(1); } }`, 300ms ease-out
- No background fill — transparent with bordered text treatment
- Badge persists until the learner navigates away

---

## 5. Interaction Summary (Lookup Table)

| Action | Element | Effect | Duration | Easing |
|--------|---------|--------|----------|--------|
| Click locked module | Module | No-op | — | — |
| Click available module | Module | Expand to 600×400 | 300ms | ease-out |
| Click X (expanded) | Close icon | Collapse to 260×180 | 300ms | ease-in |
| Click Finish knob | Knob | Rotate 135°, mark complete | 400ms | ease-out |
| Select answer | Knob | Rotate 45°, brass border | 200ms | ease-out |
| Submit correct | Wave | Upward sweep, success color | 300ms | ease-in-out |
| Submit wrong | Wave | Jagged distortion, danger | 400ms | steps |
| Timeout | Wave | Flatten to line | 500ms | ease-out |
| Question transition | Wave | Sweep down/up, wipe | 500ms | ease-in-out |
| Test complete | Wave | Large peak → settle | 600ms | ease-out |
| Path complete | All cables | Synchronous triple pulse | 500ms×3 | ease-in-out |
| Path complete | Badge | Scale in | 300ms | ease-out |
| Spiral unwind | Timer | Stroke dashoffset | 1s linear | linear (continuous updates) |

---

## 6. Component Tree (React / TSX)

```
<SignalPathWorkspace>                          // top-level container
  ├── <SignalPathRow>                          // flex container
  │   ├── <Cable from={idx} to={idx+1} />      // SVG Bézier, repeated
  │   ├── <PathModule index={i} state={s}>     // 260×180 or 600×400
  │   │   ├── <HeaderStrip state={s} />
  │   │   ├── <Jack type="input" state={s} />
  │   │   ├── <Jack type="output" state={s} />
  │   │   ├── <IconGenre type={g} state={s} />
  │   │   ├── <Title text={t} state={s} />
  │   │   ├── <WaveIndicator progress={p} state={s} />
  │   │   └── (expanded)
  │   │       ├── <CloseButton onClick={collapse} />
  │   │       ├── <VideoPlaceholder />
  │   │       ├── <ContentText />
  │   │       ├── <ExerciseList items={e} />
  │   │       └── <FinishKnob onClick={complete} />
  │   └── </PathModule>
  ├── <ProgressWave pct={pct} />               // 12px full-width waveform
  │   └── <PathPatchedBadge />                  // conditional on 100%
  └── <Oscillator visible={q}>                 // full-screen overlay
      ├── <TestName />
      ├── <SpiralTimer remaining={t} />
      ├── <QuestionText />
      ├── <WaveformDisplay state={wState} />
      ├── <AnswerKnobs>
      │   ├── <Knob label="A" value={a} />
      │   ├── <Knob label="B" value={b} />
      │   ├── <Knob label="C" value={c} />
      │   └── <Knob label="D" value={d} />
      ├── <PatchAnswerButton />
      ├── <ProgressCounter />
      └── <ScoreDisplay />                      // conditional on test end
```

---

## 7. Edge Cases & States

| Scenario | Behavior |
|----------|----------|
| Single module in path | Row renders single module; no cables shown |
| Two modules | One cable between them |
| All modules locked | Row visible, all dashed borders, no expand, progress wave flat at 0% |
| All modules completed | All success borders, progress wave at 100% + celebration, badge visible |
| Active module while others locked | Active module brass, preceding completed, following locked |
| Expand last module | Shifts left or stacks if overflow; no cable disruption |
| Test timed out mid-answer | Auto-submit partial (answered questions scored, unanswered counted wrong) |
| Network loss during test | Wave shows "Signal Lost" after 5s of no response; cached answers submitted on reconnect |
| Path with 10+ modules | Row scrolls horizontally; scrollbar hidden via `scrollbar-width: none`; mouse drag/scroll wheel scroll |
| Rapid double-click expand | Debounce 350ms; second click while animating is ignored |
| Oscillator closed mid-question | Progress saved to localStorage; resume prompt on next open |
| 0% progress | Wave is flat line across full width |
| Exactly 100% | Wave is full sine at steady amplitude; celebration triggers once |
| RTL (`dir="rtl"`) | Path row renders right-to-left; jacks swap side (input right, output left); cables Bézier control points mirrored; timer spiral rotates clockwise instead of counter-clockwise |
