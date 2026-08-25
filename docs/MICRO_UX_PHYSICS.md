# Micro-UX & Physics — Tactile Interaction Specification

> **Scope**: Cable physics (patching system), knob rotation mechanics, module dragging, LED notifications, motion design, wave breathing
> **Token dependency**: See §1.1-1.4 of [LAYOUT_NAVIGATION.md](LAYOUT_NAVIGATION.md) for shared color, spacing, typography, and border tokens
> **Absolute bans**: No gradients, no neon, no glassmorphism, no soft shadows, no border-radius > 2px on containers (50% on knobs only), no linear transitions — all motion must feel physical (springs, bounces, easing)

---

## 1. Cable Physics (Patching System)

### 1.1 Cable Rendering

- **Element**: SVG `<path>` using Bézier curve between two jack centers
- **Stroke**: `2px` solid `var(--brass)` (`#D4A843`), no dash array, solid linecap
- **Highlight**: A second `<path>` at identical curve, `0.5px` stroke, `#E8C060` (lighter brass), offset `1px` left via `transform: translate(-1px, 0)`
- **No blur, no glow** — only clean solid lines
- **No dash patterns** for any connected state

#### Bézier Formula

```
Given:
  P0 = (x1, y1)   // output jack center
  P3 = (x2, y2)   // input jack center
  dx = x2 - x1

Control points:
  cp1 = (x1 + dx * 0.4, y1)
  cp2 = (x2 - dx * 0.4, y2)

Path: M {x1} {y1} C {cp1.x} {cp1.y} {cp2.x} {cp2.y} {x2} {y2}
```

- `dx * 0.4` creates natural droop: cables bow outward proportional to distance
- When `dx <= 20px` (jacks very close): use `dx * 0.5` for tighter curve

#### SVG Structure

```svg
<g class="cable" data-cable-id="{id}" style="pointer-events: stroke;">
  <!-- Highlight layer (behind main) -->
  <path class="cable-highlight" d="..." fill="none" stroke="#E8C060"
        stroke-width="0.5" stroke-linecap="round"
        transform="translate(-1, 0)" vector-effect="non-scaling-stroke" />
  <!-- Main cable -->
  <path class="cable-main" d="..." fill="none" stroke="#D4A843"
        stroke-width="2" stroke-linecap="round"
        vector-effect="non-scaling-stroke" />
</g>
```

- `vector-effect="non-scaling-stroke"` ensures stroke width stays `2px` regardless of zoom

### 1.2 Cable Drag

#### Drag Initiation
1. `pointerdown` on an **output jack** (output jacks have `data-jack-type="output"`)
2. `event.preventDefault()` (avoid text selection)
3. Create cable SVG element with `P0 = jack center`, `P1 = pointer position`
4. `setPointerCapture(event.pointerId)` on the jack element
5. Start `requestAnimationFrame` loop

#### Drag Loop (60fps via rAF)

```javascript
let tension = 0.4;   // elasticity factor
let friction = 0.2;  // damping factor
let targetX, targetY;
let actualX, actualY; // lags behind target

function onPointerMove(event) {
  targetX = event.clientX;
  targetY = event.clientY;
}

function updateCable() {
  // Elastic lag: actual position approaches target
  actualX += (targetX - actualX) * tension;
  actualY += (targetY - actualY) * tension;
  tension *= (1 - friction); // friction decays tension slightly each frame
  tension = Math.max(0.2, tension); // but never below 0.2

  // Recalculate control points
  const dx = actualX - startX;
  const cpOffset = Math.abs(dx) * 0.4;
  const cp1x = startX + cpOffset * Math.sign(dx);
  const cp2x = actualX - cpOffset * Math.sign(dx);

  cablePath.setAttribute('d',
    `M ${startX} ${startY} C ${cp1x} ${startY} ${cp2x} ${actualY} ${actualX} ${actualY}`);

  // Check proximity to input jacks
  checkValidTargets(actualX, actualY);

  requestAnimationFrame(updateCable);
}
```

- `tension` resets to `0.4` on each new drag; `friction` remains `0.2` throughout
- When pointer is stationary > 100ms: set `tension = 1.0` (snap to cursor, no lag)
- When pointer resumes movement: `tension = 0.4` again (elastic feel resumes)

#### Valid Target Detection

- On each rAF frame, iterate all input jacks (`data-jack-type="input"`)
- For each: calculate distance from `(actualX, actualY)` to jack center
- If `distance <= 15px`: jack is "hot"
  - Add class `jack-hot` → expands to `14px` diameter circle, border `1.5px solid var(--brass)`
  - Set `data-active-target` on the cable
- If previously hot jack now `distance > 18px`: remove `jack-hot`
  - Jack returns to `10px` diameter, border `var(--text-muted)`
  - Clear `data-active-target`

#### Drop (pointerup)

**Valid drop** (over a hot input jack):
1. Snap cable endpoint to jack center in one frame (no animation)
2. Add class `cable-connected` to cable group
3. Add class `jack-connected` to both source and target jacks
4. Set `data-source-id` and `data-target-id` on cable element
5. Dispatch `patch:connect` event with `{ sourceId, targetId }`
6. Subtle settle: source and target jacks expand to `12px` for `150ms` (CSS transition: `r 150ms ease-out`), then return to `10px`

**Invalid drop** (empty space):
1. Set `tension = 0.05` (high friction) — cable freezes in place
2. Start dissolve animation: cable segments fade from tip to base
3. Implementation: overlay 8 marker points along curve at `t = 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875`
4. Fade each marker sequentially: `opacity 1 → 0` over `200ms`, staggered `25ms` apart (nearest tip first)
5. After last marker reaches opacity 0: remove cable element entirely (`200ms` total)
6. Dispatch `patch:disconnect-abort` event

### 1.3 Cable States

| State | Main Stroke | Highlight | Thickness | Interaction |
|-------|-------------|-----------|-----------|-------------|
| **Connected** | `#D4A843` solid | Visible, `#E8C060` | `2px` | None |
| **Hover** (mouse over cable) | `#E0B84C` solid | Visible, `#E8C060` | `3px` | `cursor: pointer` |
| **Selected** (clicked once) | `#D4A843` solid | Visible | `2px` | Both endpoint jacks show an offset ring: `1px solid var(--brass)` circle `4px` outside jack, `r=14px`, no blur, no fill |
| **Error** | `#C8553D` solid | Hidden | `2px` | Flashes: `var(--danger)` for `300ms`, back to `#D4A843` for `100ms`, repeat 3× total. After 3rd flash: cable stays `#D4A843`. Dispatch `patch:error` |
| **Dragging** | `#E0B84C` | Visible | `2.5px` | Cable follows cursor with elastic lag |

### 1.4 Cable Disconnect

#### Double-click on Cable
1. `dblclick` on cable group → small disconnect icon appears at cable midpoint
2. `midpoint = (P0 + P3) / 2` (average of start and end points) — exact curve midpoint

```
.disconnect-btn {
  position: absolute;
  width: 16px; height: 16px;
  background: var(--danger);
  border: none;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  /* crosshair X via two pseudo-element lines */
  border-radius: 0; /* no radius on container; individual pseudo-lines */
  opacity: 0;
  transition: opacity 100ms ease-out;
  z-index: 100;
}
.disconnect-btn.visible { opacity: 1; }
```

- X lines: two `1.5px` thick lines, `#0B0B0D` (bg-root), rotated `45deg` and `-45deg`, `8px` length each
- Positioned at cable midpoint using `left`/`top` CSS (computed from SVG midpoint coordinates)
- Applied as absolutely-positioned `<div>` inside the SVG container, not inside the SVG itself (avoids coordinate transform issues)

#### Click Disconnect Button
1. Cable disintegrates: 6-8 small particles scatter from multiple points along curve
2. Particle generation: sample 6-8 points along Bézier at `t = 0.1, 0.25, 0.4, 0.55, 0.7, 0.85`
3. At each point: create a `<circle>` element (`3px` diameter, `var(--brass)`) with CSS animation:
   - `translate` outward `30-60px` in random direction (uniform distribution, all 360°)
   - `opacity` 1→0
   - Duration: `400ms` ease-out
   - Particle removal: `setTimeout(() => particle.remove(), 400)`
4. Cable main path: fade `opacity 1→0` over `300ms` (faster than particles)
5. Highlight path: fade `opacity 1→0` over `200ms`
6. After `450ms`: full cable group removed, `jack-connected` removed from both jacks
7. Dispatch `patch:disconnect` event with `{ sourceId, targetId }`

#### Right-click Context Menu
1. `contextmenu` on cable → prevent default browser menu
2. Show custom context menu at pointer position:
   - `width: 120px`, `background: var(--surface)`, `border: 1px solid var(--border)`
   - Option: "Cut Patch" (`height: 32px`, `color: var(--danger)`)
   - Option: "Cancel" (`height: 32px`, `color: var(--text-primary)`)
   - Hover on "Cut Patch": background `rgba(200, 85, 61, 0.08)`
3. Click "Cut Patch": same disintegration as §1.4.2
4. Click elsewhere or "Cancel": remove context menu

### 1.5 Module Move Cable Recalculation

#### Connected Module Dragged
1. On `module:drag-start`: collect all cables where `data-source-id === moduleId` or `data-target-id === moduleId`
2. During drag (rAF loop at 60fps): for each connected cable, recalculate:
   - Read current jack positions: `getBoundingClientRect()` on source/target jack elements
   - Update `P0` and `P3` to new jack centers
   - Recalculate control points using same `dx * 0.4` formula
   - Set `d` attribute directly — no animation, smooth update
3. No snapping during cable update — Bézier interpolates naturally

#### Stretch and Break
1. If module is dragged beyond workspace bounds (module center outside `#workspace` rect):
   - Cable stretches: control points extend further (cap `dx` factor at `2.0 × distance` max)
   - If module remains outside bounds for `> 2000ms`: cable auto-disconnects
   - Auto-disconnect: flash `var(--danger)` for `300ms`, then same disintegration as §1.4.2 but without particle scatter (just fade out `200ms`)
   - Dispatch `patch:break` event with `{ sourceId, targetId, reason: 'out-of-bounds' }`
2. If module is rapidly dragged far (> 500px in < 100ms): cable breaks immediately with warning flash (`var(--danger)` 150ms, 2 flashes, then removed)

---

## 2. Knob Behavior

### 2.1 Knob Sizing

| Size | Diameter | Usage | Indicator Length | Tick Marks |
|------|----------|-------|-----------------|------------|
| Large | `56px` | Statistics, main controls | `12px` from center | `12` ticks |
| Medium | `40px` | Navigation, primary interactions | `8px` from center | `10` ticks |
| Small | `24px` | Fine-tuning, secondary controls | `5px` from center | `8` ticks |
| Tiny | `16px` | Rare inline adjustments | `3px` from center | `6` ticks |

### 2.2 Knob Construction

#### Base Element (Medium 40px as example)

```css
.knob {
  position: relative;
  width: 40px; height: 40px;
  border-radius: 50%;
  background: var(--surface);
  border: 1.5px solid var(--text-muted);
  cursor: ns-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: border-color 100ms ease-out, background 100ms ease-out;
}
```

#### Knurled Edge

```css
.knob::before {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: 50%;
  background: repeating-conic-gradient(
    #5A5854 0deg 1.5deg,
    transparent 1.5deg 3deg
  );
  opacity: 0;
  pointer-events: none;
  transition: opacity 100ms ease-out;
}
```

- `10` ticks for medium: each tick `1.5deg` wide, `1.5deg` gap → `3deg` per cycle × 10 = `30deg` but spread across full circle = repeating-conic over full 360°
  - Actually: `360deg / 10 = 36deg` per tick cycle. Use `36deg` step: `repeating-conic-gradient(#5A5854 0deg 1.5deg, transparent 1.5deg 36deg)`
  - Large (12 ticks): `360 / 12 = 30deg` → `repeating-conic-gradient(#5A5854 0deg 1.5deg, transparent 1.5deg 30deg)`
  - Small (8 ticks): `360 / 8 = 45deg` → `repeating-conic-gradient(#5A5854 0deg 1.5deg, transparent 1.5deg 45deg)`
  - Tiny (6 ticks): `360 / 6 = 60deg` → `repeating-conic-gradient(#5A5854 0deg 1.5deg, transparent 1.5deg 60deg)`

- Opacity controlled by state (see §2.4)

#### Indicator Line

```html
<svg class="knob-indicator" viewBox="0 0 {size} {size}" width="{size}" height="{size}"
     style="position: absolute; top: 0; left: 0; pointer-events: none;">
  <line x1="{size/2}" y1="{size/2}"
        x2="{size/2}" y2="{size/2 - indicatorLength}"
        stroke="#D4A843" stroke-width="2" stroke-linecap="round"
        transform="rotate({rotationDeg}, {size/2}, {size/2})" />
</svg>
```

Indicator lengths by size:
- 56px: center `(28,28)`, indicator `y2=16` (12px line)
- 40px: center `(20,20)`, indicator `y2=12` (8px line)
- 24px: center `(12,12)`, indicator `y2=7` (5px line)
- 16px: center `(8,8)`, indicator `y2=5` (3px line)

#### Center Dot

```css
.knob-center {
  width: 3px; height: 3px;
  border-radius: 50%;
  background: var(--brass);
  pointer-events: none;
  z-index: 1;
}
```

- Constant `3px` dot regardless of knob size
- Color always `var(--brass)` — no state change

### 2.3 Rotation Mechanics

#### Input Methods

| Method | Mapping |
|--------|---------|
| **Vertical drag** | `1px` vertical = `0.5°` rotation. `clientY` decreasing = increase. `clientY` increasing = decrease. |
| **Scroll wheel** | `1` tick = `5°` rotation. Accumulate `deltaY`. `deltaY < 0` = increase. |
| **Touch drag** | Same as vertical drag via `touchmove`. `touchstart` stores `startY`. |

#### Drag Interaction (pointer events)

```
pointerdown on knob:
  - setPointerCapture(pointerId)
  - store startY = event.clientY
  - store startRotation = currentRotation
  - add class 'active'
  - show tooltip
  - dispatch knob:interaction-start

pointermove:
  - dy = startY - event.clientY
  - newRotation = startRotation + (dy * 0.5)
  - clamp to [-135, 135]
  - update indicator SVG transform
  - update tooltip content
  - if value changed: dispatch knob:value-change

pointerup:
  - releasePointerCapture()
  - remove class 'active'
  - start tooltip fade timer (500ms)
  - dispatch knob:interaction-end
```

#### Scroll Wheel Interaction

```
wheel on knob (passive: false):
  - preventDefault()
  - accumulator += event.deltaY
  - while accumulator >= 100: one tick (+5°), accumulator -= 100
  - while accumulator <= -100: one tick (-5°), accumulator += 100
  - clamp rotation to [-135, 135]
  - update indicator and tooltip
  - reset idle timeout (tooltip stays visible)
  - on idle 500ms: fade tooltip
```

#### Rotation Range

- **Origin**: `0°` = indicator pointing straight up (12 o'clock)
- **Range**: `-135°` (counter-clockwise min) to `+135°` (clockwise max)
- **Total sweep**: `270°`
- **Resolution**: continuous (any float degree within range)
- **Display value**: rounded to integer percentage `(rotation + 135) / 270 * 100`

### 2.4 Knob States

| State | Border | Knurl Opacity | Center Dot | Background | Cursor |
|-------|--------|---------------|------------|------------|--------|
| **Default** | `1.5px solid var(--text-muted)` | `0` | `var(--brass)` | `var(--surface)` | default |
| **Hover** | `1.5px solid var(--brass)` | `0.3` | `var(--brass)` | `var(--surface)` | `ns-resize` |
| **Active (turning)** | `1.5px solid var(--brass)` | `0.5` | `var(--brass)` | `#1E1E22` | `ns-resize` |
| **At limit** | `1.5px solid var(--brass)` | `0.5` | `var(--brass)` | `#1E1E22` | `ns-resize` |
| **Disabled** | `1.5px solid var(--text-muted)` | `0` | `var(--text-muted)` `opacity: 0.4` | `var(--surface)` `opacity: 0.4` | not-allowed |
| **Focus-visible** | `1.5px solid var(--brass)` | `0.3` | `var(--brass)` | `var(--surface)` | default |

#### At-Limit Vibration

When rotation reaches exactly `-135°` or `+135°`:
1. Trigger vibration: rapid horizontal oscillation on knob element
2. `transform: translateX(0)` → `translateX(3px)` → `translateX(-3px)` → `translateX(0)` → `translateX(3px)` → `translateX(-3px)` → `translateX(0)`
3. Each step = `12.5ms` (total `100ms` for 4 cycles)
4. Implemented via `requestAnimationFrame` with time stepping:

```javascript
function vibrateKnob(knobEl) {
  const start = performance.now();
  const duration = 100; // ms
  const amplitude = 3; // px
  let frame;

  function step(now) {
    const elapsed = now - start;
    if (elapsed >= duration) {
      knobEl.style.transform = 'translateX(0)';
      return;
    }
    const cycle = Math.sin(elapsed / duration * Math.PI * 8); // 4 full cycles
    knobEl.style.transform = `translateX(${cycle * amplitude}px)`;
    frame = requestAnimationFrame(step);
  }
  frame = requestAnimationFrame(step);
}
```

#### Disabled Override

```css
.knob[data-disabled="true"] {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}
```

- Active+disabled is not possible — disabled knobs cannot receive interaction

### 2.5 Value Mapping

#### Continuous Values (0-100)

```
normalizedValue = (rotation + 135) / 270  // 0.0 to 1.0
displayValue = Math.round(normalizedValue * 100)
tooltipContent = `${displayValue}%`
```

#### Arbitrary Range (min, max)

```
valueRange = max - min
currentValue = min + normalizedValue * valueRange
displayValue = Math.round(currentValue * 10) / 10  // 1 decimal
tooltipContent = `${displayValue}`
```

#### Enum/Discrete Values

```
enumValues = ['Saw', 'Square', 'Triangle', 'Sine']
enumIndex = Math.round(normalizedValue * (enumValues.length - 1))
tooltipContent = `${enumValues[enumIndex]} · ${enumIndex + 1}/${enumValues.length}`
```

**Detents**: When dragging past an enum boundary, a brief snap animation:
1. At exact boundary crossing: `transform: scale(1.05)` over `25ms` ease-out, then back to `scale(1)` over `25ms`
2. Total `50ms` — feels like a mechanical detent click
3. Dispatch `knob:detent` event with `{ index: enumIndex }`

### 2.6 Numeric Tooltip (Value Readout)

#### Positioning

```css
.knob-tooltip {
  position: fixed;
  top: calc(var(--knob-top) - 24px); /* 24px above knob top edge */
  left: calc(var(--knob-left) + var(--knob-size) / 2);
  transform: translateX(-50%);
  background: var(--surface);
  border: 1px solid #2A2A2E;
  padding: 2px 8px;
  font-family: JetBrains Mono;
  font-size: 11px;
  color: var(--brass);
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 200ms ease;
  z-index: 1100;
}
.knob-tooltip.visible { opacity: 1; }
```

- `--knob-top`, `--knob-left`, `--knob-size` set as inline style vars on the tooltip element
- Computed on each drag frame: `knobEl.getBoundingClientRect()`
- Format: varies by mapping:
  - Continuous 0-100: `"70%"`
  - Enum: `"Sine · 3/4"`
  - Time: `"7d 3h"`
  - Generic: `"3/10"` (for arbitrary range with max shown)

#### Lifecycle

1. **Show**: First interaction (pointerdown, wheel tick). Add `visible` class. Clear any existing fade timer.
2. **During interaction**: Update content in real-time on each event. Keep `visible`.
3. **Hide**: `500ms` after last interaction event (`pointerup` or last `wheel` event + debounce). Start fade: remove `visible` class → CSS transitions `opacity` from 1→0 over `200ms`. After `200ms`: optionally hide (`display: none`) but not required if `pointer-events: none`.

---

## 3. Module Dragging

### 3.1 Drag Handle

```
.module-drag-handle {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 8px;
  background: var(--surface);
  border-bottom: 1px solid transparent;
  cursor: grab;
  transition: background 100ms ease-out, border-bottom-color 100ms ease-out;
  z-index: 1;
}
```

| State | Background | Border-bottom | Cursor |
|-------|------------|---------------|--------|
| **Default** | `var(--surface)` | `transparent` | `grab` |
| **Hover** | `var(--brass)` | `transparent` | `grab` |
| **Active (dragging)** | `var(--brass)` | `1px solid #B89230` (darker brass) | `grabbing` |

### 3.2 Drag Mechanics

#### Initiation

```
pointerdown on .module-drag-handle:
  - setPointerCapture(pointerId)
  - store startX, startY
  - store module's current gridPosition (data-x, data-y in px)
  - add class 'module-dragging' to module
  - module rises: transform: translateY(-2px) OR z-index bump to 100 (whichever fits architecture)
  - dispatch module:drag-start { id, x, y }
  - dim all OTHER modules to opacity 0.95:
    document.querySelectorAll('.module:not(.module-dragging)').forEach(m => {
      m.style.opacity = '0.95';
      m.style.transition = 'opacity 150ms ease-out';
    })
```

No shadow is added on lift — consistent with the no-blur ban.

#### During Drag

```
pointermove:
  - dx = event.clientX - startX
  - dy = event.clientY - startY
  - newX = gridStartX + dx
  - newY = gridStartY + dy
  - module.style.left = newX + 'px'
  - module.style.top = newY + 'px'
  - NO grid snapping during drag — free movement
  - dispatch module:drag-move { id, x: newX, y: newY }
```

#### Grid Snapping on Drop

```
pointerup:
  - releasePointerCapture()
  - snapX = Math.round(newX / 40) * 40
  - snapY = Math.round(newY / 40) * 40
  - Animate to snap:
    module.style.transition = 'left 150ms ease-out, top 150ms ease-out'
    module.style.left = snapX + 'px'
    module.style.top = snapY + 'px'
  - Bounce: on transitionend (150ms):
    // Brief overshoot via transform
    const bounce = [
      { transform: 'translateY(-2px)' },
      { transform: 'translateY(0)' }
    ];
    module.animate(bounce, { duration: 50, easing: 'ease-out' });
    // After bounce:
    module.style.transition = ''
    module.style.transform = ''
    // Remove drag state
    module.classList.remove('module-dragging')
    // Restore other modules
    document.querySelectorAll('.module').forEach(m => {
      m.style.opacity = '';
      m.style.transition = '';
    })
    // Update data attributes
    module.dataset.x = snapX;
    module.dataset.y = snapY;
    // Dispatch
    dispatch module:drag-end { id, x: snapX, y: snapY }
```

- Snap animation: `150ms ease-out` — positions jump to grid point
- Bounce: `50ms` ease-out, `translateY(-2px)` overshoot then settle
- Bounce only occurs if the module moved more than `20px` from start position
- If snap is same as start position (no movement): no bounce, no animation, instant snap

#### Invalid Drop (Outside Workspace)

1. If `newX < -100 || newY < -100 || newX > workspaceWidth + 100 || newY > workspaceHeight + 100`:

```javascript
module.style.transition = 'left 200ms ease-out, top 200ms ease-out';
module.style.left = originalX + 'px';
module.style.top = originalY + 'px';
module.classList.remove('module-dragging');
// On transitionend:
module.style.transition = '';
module.dataset.x = originalX;
module.dataset.y = originalY;
dispatch module:drag-cancel { id }
```

- Module animates smoothly back to original grid position over `200ms` ease-out
- No bounce on return

### 3.3 Drop Behavior

#### Rack Detection Check

On drop (before snap animation):
1. Check if module center falls within any rack boundary
2. Racks are `<div class="rack">` elements with `getBoundingClientRect()`
3. If inside a rack: auto-align to nearest available position in that rack (horizontal row)
4. Rack auto-align: find next open slot in the rack's flex layout
   - Remove module from `position: absolute` flow
   - Append as flex child of rack (absolute positioning relative to rack container)
   - Re-flow rack layout
   - Use `transition: order 150ms ease-out` or `transform` for smooth insertion

#### Valid Drop Recovery

1. After snap animation (`150ms`): module stays raised `2px` for `200ms` more
2. Then settles: `transform: translateY(0)` over `100ms` ease-out
3. Full duration from drop to settle: `150ms` snap + `200ms` hold + `100ms` settle = `450ms`

### 3.4 Module Z-Index During Drag

```css
.module-dragging {
  z-index: 100 !important;
  transition: none; /* disable all transitions during drag */
}
```

- All other modules: unaffected z-index (keep their original z-ordering)
- On drag end: `z-index` returns to original value (set via `data-z` attribute or original computed value)

---

## 4. LED Notifications

### 4.1 LED Construction

```css
.led {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 1px solid #1A1A1A;
  background: #1A1A1A; /* off */
  flex-shrink: 0;
  box-sizing: border-box;
}

/* On state: border matches color */
.led.on {
  border-color: var(--teal);
  background: var(--teal);
}
```

- `8px` diameter circle, `1px` border
- No glow, no blur, no box-shadow — pure solid color
- Border defaults to `#1A1A1A` when off, adopts LED color when on

### 4.2 LED States

| State | Background | Border | Animation |
|-------|------------|--------|-----------|
| **Off** | `#1A1A1A` | `#1A1A1A` | None |
| **Normal** | `var(--teal)` | `var(--teal)` | Slow pulse: `scale 1.0 → 1.2 → 1.0`, `2s` cycle, opacity constant |
| **Attention** | `var(--brass)` | `var(--brass)` | Medium pulse: `scale 1.0 → 1.3 → 1.0`, `1s` cycle, opacity constant |
| **Alert** | `var(--danger)` | `var(--danger)` | Fast blink: `on 200ms` + `off 200ms`, repeat 3×, then pause `3s`, repeat cycle |
| **Solid Alert** | `var(--danger)` | `var(--danger)` | Solid on, no animation (for persistent error states) |
| **Error** | `var(--danger)` | `var(--danger)` | Solid, continuous — never animates |

#### Pulse Animations

```css
@keyframes led-pulse-normal {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.2); }
}
@keyframes led-pulse-attention {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.3); }
}

.led.normal   { animation: led-pulse-normal   2s ease-in-out infinite; }
.led.attention { animation: led-pulse-attention 1s ease-in-out infinite; }
```

#### Alert Blink (JavaScript driven)

```javascript
function blinkAlert(ledEl, times = 3) {
  let count = 0;
  const interval = setInterval(() => {
    ledEl.style.background = '#1A1A1A'; // off
    ledEl.style.borderColor = '#1A1A1A';
    setTimeout(() => {
      ledEl.style.background = 'var(--danger)';
      ledEl.style.borderColor = 'var(--danger)';
    }, 200);
    count++;
    if (count >= times) {
      clearInterval(interval);
      setTimeout(() => {
        // Reset to solid on for pause
        ledEl.style.background = 'var(--danger)';
        ledEl.style.borderColor = 'var(--danger)';
        // After 3s pause, repeat if still in alert state
        if (ledEl.dataset.ledState === 'alert') {
          blinkAlert(ledEl, times);
        }
      }, 3000);
    }
  }, 400); // 200 on + 200 off
}
```

---

## 5. General Motion Design

### 5.1 Transition Timing Table

| Interaction | Duration | Easing | Application |
|-------------|----------|--------|-------------|
| **Micro-interactions** | `100ms` | `ease-out` | Hover states, focus rings, knob drag start/stop, button press, LED on/off |
| **Normal transitions** | `300ms` | `ease-out` | Module expand, drawer slide, cable connect, section wipe partially, panel reveal |
| **Macro transitions** | `400ms` | `ease-in-out` | Full section wipe (workspace replace), mode switch, workspace clear/reset |
| **Celebration** | `600ms` | `ease-out` | Path complete particle burst, achievement unlock, milestone reached |
| **Snap/bounce** | `150ms` | `ease-out` | Grid snap on drop, rack alignment, detent snap |
| **Tooltip fade** | `200ms` | `ease` | Tooltip opacity 1→0 |
| **Cable connect settle** | `150ms` | `ease-out` | Jack expansion after valid drop |

### 5.2 CSS Transition Implementation

```css
:root {
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.76, 0, 0.24, 1);
  --ease-bounce: cubic-bezier(0.34, 1.5, 0.64, 1);
}
```

- `cubic-bezier(0.16, 1, 0.3, 1)` — custom ease-out (slightly overshooting, physical feel)
- `cubic-bezier(0.76, 0, 0.24, 1)` — custom ease-in-out (symmetric, smooth)
- `cubic-bezier(0.34, 1.5, 0.64, 1)` — bounce-like (overshoots target, settles back)

### 5.3 Animation Methods Matrix

| Technique | When to Use | Implementation |
|-----------|-------------|----------------|
| **CSS transitions** | Color changes, opacity, simple transforms (scale, rotate, translateX/Y) | `transition: property duration easing` |
| **CSS animations** | Looping effects (LED pulse, wave breathing), keyframe sequences | `@keyframes` + `animation` |
| **requestAnimationFrame** | Cable physics, drag operations, particle systems, rAF-driven wave | `requestAnimationFrame(updateFn)` loop |
| **SVG `<animate>`** | Wave indicator oscilloscope traces, path morphing | `<animate attributeName="d" ...>` |
| **Web Animations API** | One-shot animations (detent, bounce, particle scatter) | `element.animate(keyframes, options)` |

### 5.4 Ground Rules

1. **No `transition: all`** — always specify properties explicitly
2. **No animation libraries** — use CSS + native JS only
3. **Transform-based animations** for GPU acceleration (translate, scale, rotate) over layout-triggering properties (left, top, width, height)
4. Exception: module drag uses `left`/`top` for grid-position; this is acceptable as position is static most of the time
5. `will-change: transform` on elements that animate frequently (during drag only, via JS)

### 5.5 Wave Breathing

#### Every Wave Indicator at Rest

Even when no signal is passing, every wave/oscilloscope trace "breathes" — a subtle, barely-perceptible amplitude oscillation.

- **Frequency**: `0.5Hz` (one full cycle every `2s`)
- **Amplitude**: `±2%` of wave height — virtually invisible but feels alive
- **Phase**: each wave element has a staggered phase offset: `elementIndex * 0.5` radians (so they don't pulse in unison)

#### CSS Implementation

```css
@keyframes wave-breathe {
  0%   { transform: scaleY(1); }
  50%  { transform: scaleY(1.02); }
  100% { transform: scaleY(1); }
}

.wave-indicator {
  transform-origin: center center;
  animation: wave-breathe 2s ease-in-out infinite;
}
```

#### Per-element Phase Offset (JS)

```javascript
document.querySelectorAll('.wave-indicator').forEach((el, i) => {
  const delay = (i * 0.5) / (Math.PI * 2) * 2; // convert rad phase to seconds
  el.style.animationDelay = `-${delay}s`;
});
```

#### SVG Path Implementation (for oscilloscope traces)

```html
<svg viewBox="0 0 200 60" class="wave-indicator">
  <path class="wave-path" d="M0 30 Q 25 10 50 30 T 100 30 T 150 30 T 200 30"
        fill="none" stroke="var(--teal)" stroke-width="1.5"
        vector-effect="non-scaling-stroke">
    <animate attributeName="d" dur="2s" repeatCount="indefinite"
             values="
               M0 30 Q 25 10 50 30 T 100 30 T 150 30 T 200 30;
               M0 30 Q 25 12 50 30 T 100 30 T 150 30 T 200 30;
               M0 30 Q 25 10 50 30 T 100 30 T 150 30 T 200 30" />
  </path>
</svg>
```

- The `values` alternates between the base path and a path with `2px` Y-offset on control points
- Phase offset: use `<animate>` `begin` attribute with staggered times, or JS `beginElement()` timing
- For multiple waves: offset start times by `elementIndex * 0.5s`

---

## 6. Event Bus Additions

Events dispatched by this module (in addition to those in LAYOUT_NAVIGATION.md §11):

| Event | Detail | Trigger |
|-------|--------|---------|
| `patch:connect` | `{ sourceId, targetId }` | Cable connected |
| `patch:disconnect` | `{ sourceId, targetId }` | Cable disconnected (manual) |
| `patch:disconnect-abort` | `{}` | Cable drag dropped on empty space |
| `patch:break` | `{ sourceId, targetId, reason }` | Cable broke due to stretch or speed |
| `patch:error` | `{ sourceId, targetId }` | Connection error detected |
| `knob:interaction-start` | `{ knobId, value }` | Knob drag/scroll begins |
| `knob:interaction-end` | `{ knobId, value }` | Knob interaction ends |
| `knob:value-change` | `{ knobId, value, rotation }` | Knob value changed |
| `knob:detent` | `{ knobId, index }` | Knob crossed discrete detent boundary |
| `module:drag-start` | `{ id, x, y }` | Module drag begins |
| `module:drag-move` | `{ id, x, y }` | Module drag in progress |
| `module:drag-end` | `{ id, x, y }` | Module dropped and snapped |
| `module:drag-cancel` | `{ id }` | Module drag cancelled (outside bounds) |

---

## 7. Performance Budget

| Operation | Budget | Measurement |
|-----------|--------|-------------|
| Cable physics update per frame | `< 0.5ms` | All connected cables during module drag |
| Knob rotation per event | `< 0.3ms` | Single knob rotation recalculation |
| Module drag per frame | `< 1ms` | Moving module + recalculating N cables |
| Particle system (disintegration) | `< 2ms` | 8 particles animating |
| rAF callback total | `< 3ms` | All physics + rendering per frame |
| Frame rate target | `60fps` (≤ 16.6ms per frame) | Monitor via `performance.now()` |

---

## 8. CSS Custom Properties Additions

```css
:root {
  /* Existing tokens from LAYOUT_NAVIGATION.md - not redefined here */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.76, 0, 0.24, 1);
  --ease-bounce: cubic-bezier(0.34, 1.5, 0.64, 1);

  /* Cable */
  --cable-stroke: 2px;
  --cable-color: var(--brass);
  --cable-highlight: #E8C060;
  --cable-hover-color: #E0B84C;
  --cable-error-color: var(--danger);

  /* Knob */
  --knob-large: 56px;
  --knob-medium: 40px;
  --knob-small: 24px;
  --knob-tiny: 16px;
  --knob-indicator-width: 2px;
  --knob-center-size: 3px;

  /* LED */
  --led-size: 8px;
  --led-off: #1A1A1A;
  --led-pulse-normal: 2s;
  --led-pulse-attention: 1s;

  /* Timing */
  --micro: 100ms;
  --normal: 300ms;
  --macro: 400ms;
  --celebration: 600ms;
  --snap: 150ms;
  --tooltip-fade: 200ms;

  /* Grid */
  --grid-unit: 40px;
}
```

---

## 9. Implementation Checklist

- [ ] Cable Bézier rendering (SVG path, highlight, no blur)
- [ ] Cable drag: elastic physics (tension 0.4, friction 0.2, rAF 60fps)
- [ ] Valid target detection (15px radius, jack expands to 14px)
- [ ] Invalid drop dissolve (8 marker points, sequential fade 200ms)
- [ ] Cable states: connected, hover (3px + #E0B84C), selected (offset ring), error (3× flash)
- [ ] Double-click disconnect: X icon at midpoint, particle scatter (6-8 dots, 400ms)
- [ ] Right-click context menu: "Cut Patch" + disintegration
- [ ] Module move cable recalculation (rAF, all connected cables)
- [ ] Stretch/break: 2000ms out-of-bounds timeout, rapid-move break
- [ ] Knob construction: 4 sizes (56/40/24/16), knurled edge conic-gradient, indicator line SVG, center dot
- [ ] Rotation: vertical drag (0.5°/px) + scroll wheel (5°/tick), -135° to +135°
- [ ] Knob states: default/hover/active/limit/disabled/focus
- [ ] At-limit vibration: 3px oscillation, 4 cycles, 100ms total
- [ ] Value mapping: continuous 0-100, arbitrary range, enum with detents (50ms snap)
- [ ] Numeric tooltip: 16px above, JetBrains Mono, 500ms fade
- [ ] Module drag handle: 8px strip, brass on hover/active
- [ ] Drag mechanics: lift 2px, dim others to 0.95, free movement
- [ ] Grid snap: 40px units, 150ms ease-out + 2px overshoot bounce
- [ ] Invalid drop recovery: animate back 200ms
- [ ] Rack detection: auto-align to flex row on drop
- [ ] LED construction: 8px, 1px border, solid color
- [ ] LED states: off, normal (2s pulse), attention (1s pulse), alert (200ms blink ×3 + 3s pause), error (solid)
- [ ] Transition timings: micro 100ms, normal 300ms, macro 400ms, celebration 600ms, snap 150ms
- [ ] Custom easings: ease-out `(0.16, 1, 0.3, 1)`, ease-in-out `(0.76, 0, 0.24, 1)`, bounce `(0.34, 1.5, 0.64, 1)`
- [ ] Wave breathing: 0.5Hz, ±2% amplitude, staggered phase offsets
- [ ] Event bus: all 14 events implemented
- [ ] Performance: rAF callback < 3ms, 60fps target
- [ ] CSS custom properties: all additions listed in §8 defined in `:root`
