# SkillSynth — Modular Synthesizer Design System

> **Platform redefinition**: A modular analog synthesizer (Eurorack) learning platform. Every element translates a physical synth component into a functional UI.
> **Absolute bans**: No gradients. No neon/glow. No glassmorphism. No soft shadows (box-shadow blur > 0). No border-radius > 2px on containers (50% on knobs only). No traditional sidebar. No standard charts/tables. No generic SaaS dashboard.
> **Implementation status**: Complete design specification ready for development.

---

## Table of Contents

1. [Comprehensive Visual System (Agent 6)](#1-comprehensive-visual-system)
2. [Global Layout & Navigation (Agent 1)](#2-global-layout--navigation)
3. [Learner Experience (Agent 2)](#3-learner-experience)
4. [Manager Studio (Agent 3)](#4-manager-studio)
5. [Admin Central Laboratory (Agent 4)](#5-admin-central-laboratory)
6. [Micro-Interaction & Physics System (Agent 5)](#6-micro-interaction--physics-system)
7. [Responsive Design (Agent 7)](#7-responsive-design)
8. [Integration Audit & Completeness (Agent 8)](#8-integration-audit--completeness)

---

## 1. Comprehensive Visual System

### 1.1 Mandatory Design Tokens (Immutable)

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-root` | `#0B0B0D` | Infinite workspace background |
| `--surface` | `#16161A` | Module surfaces, drawers, panels |
| `--brass` | `#D4A843` | Primary interactions, patch cables, active knobs, highlights |
| `--teal` | `#3D5A5C` | Learning paths, statistics, calm indicators |
| `--text-primary` | `#F5F0E7` | Primary text on dark surfaces |
| `--text-muted` | `#8A8882` | Secondary text, idle borders |
| `--success` | `#6A8A5C` | Completion, success, stable wave |
| `--danger` | `#C8553D` | Errors, warnings, signal noise |

### 1.2 Complete Color Palette

#### Surface & Background
| Token | Value | Usage |
|-------|-------|-------|
| `--bg-root` | `#0B0B0D` | Root workspace, modal backdrop |
| `--surface` | `#16161A` | Module body, drawer, panel, card |
| `--surface-hover` | `#1E1E22` | Module hover, list item hover |
| `--surface-active` | `#222228` | Pressed state, selected item |
| `--surface-elevated` | `#1A1A1E` | Modal, dropdown, tooltip |
| `--surface-contrast` | `#111115` | Overlay, backdrop |
| `--surface-input` | `#131317` | Text input, textarea |

#### Accents
| Token | Value | Usage |
|-------|-------|-------|
| `--brass` | `#D4A843` | Primary accent, cable default |
| `--brass-dim` | `#A58736` | Disabled brass, inactive accent |
| `--brass-light` | `#E8C56E` | Brass hover, glow center |
| `--teal` | `#3D5A5C` | Secondary accent, LED idle |
| `--teal-bright` | `#4F7A7D` | Teal hover, active state |
| `--teal-dim` | `#2E4446` | Teal disabled, muted accent |

#### Signals
| Token | Value | Usage |
|-------|-------|-------|
| `--success` | `#6A8A5C` | Complete, positive states |
| `--success-bright` | `#7EA66E` | Success hover |
| `--danger` | `#C8553D` | Error, urgent LED, cable error |
| `--danger-bright` | `#E06A50` | Danger hover, blink active |
| `--warning` | `#C8943D` | Warning, near-limit states |
| `--warning-bright` | `#DBA94E` | Warning hover |

#### Text
| Token | Value | Usage |
|-------|-------|-------|
| `--text-primary` | `#F5F0E7` | Body text, headings |
| `--text-secondary` | `#C4BFB4` | Secondary text, descriptions |
| `--text-muted` | `#8A8882` | Placeholder, caption, meta |
| `--text-disabled` | `#5A5854` | Disabled text, inactive labels |
| `--text-on-brass` | `#0B0B0D` | Text on brass backgrounds |

#### Borders
| Token | Value | Usage |
|-------|-------|-------|
| `--border-subtle` | `#2A2A2E` | Default module border, jack border |
| `--border-brass` | `#D4A843` | Active selection, focus ring |
| `--border-error` | `#C8553D` | Error state, validation fail |
| `--border-success` | `#6A8A5C` | Success state, completed |
| `--border-hover` | `#4A4A50` | Hover state on borders |

#### Component-Specific
| Token | Value | Usage |
|-------|-------|-------|
| `--knob-body` | `#16161A` | Knob surface |
| `--knob-indicator` | `#D4A843` | Knob position line |
| `--knob-rim` | `#2A2A2E` | Knob outer rim |
| `--led-off` | `#1A1A1A` | LED powered down |
| `--led-idle` | `#3D5A5C` | LED idle (teal pulse) |
| `--jack-idle` | `#16161A` | Jack surface idle |
| `--jack-rim` | `#2A2A2E` | Jack outer ring |
| `--jack-connected` | `#D4A843` | Jack fill when connected |
| `--cable-default` | `#D4A843` | Patch cable body |
| `--cable-hover` | `#E8C56E` | Cable on hover |
| `--cable-error` | `#C8553D` | Cable with routing error |

### 1.3 Typography

#### Font Families
| Token | Font | Weights | Usage |
|-------|------|---------|-------|
| `--font-heading` | `'IBM Plex Sans', 'IBM Plex Sans Arabic', sans-serif` | 600 | Headings, controls, labels |
| `--font-body` | `'Tajawal', sans-serif` | 400, 500 | Body text, descriptions |
| `--font-mono` | `'JetBrains Mono', monospace` | 400, 500, 600 | Numeric displays, code, data |

#### Type Scale
| Size | Rem | Usage |
|------|-----|-------|
| 10px | 0.625rem | Caption, metadata, jack labels |
| 12px | 0.75rem | Small UI, LED status, tags |
| 14px | 0.875rem | Body small, knob labels, inputs |
| 16px | 1rem | Body default, paragraphs |
| 18px | 1.125rem | Module title, nav item |
| 24px | 1.5rem | Section heading H3 |
| 32px | 2rem | Page heading H2 |
| 48px | 3rem | Hero heading H1 |

#### Line Heights
| Usage | Value |
|-------|-------|
| Tight (headings, labels) | 1.1 |
| Normal (body) | 1.4 |
| Relaxed (notes) | 1.6 |
| Mono (data) | 1.2 |

#### Letter Spacing
| Usage | Value |
|-------|-------|
| Tech heading (48/32px) | `-0.02em` |
| Section heading (24px) | `-0.01em` |
| Control label | `0.02em` |
| Uppercase label | `0.08em` |
| Arabic headings | `0em` (no tracking in Arabic) |

#### Composed Text Tokens
```
--text-hero:       48px / 1.1 var(--font-heading);
--text-h1:         32px / 1.1 var(--font-heading);
--text-h2:         24px / 1.1 var(--font-heading);
--text-body:       16px / 1.4 var(--font-body);
--text-body-sm:    14px / 1.4 var(--font-body);
--text-label:      14px / 1.1 var(--font-heading);
--text-mono:       16px / 1.2 var(--font-mono);
--text-mono-xs:    12px / 1.2 var(--font-mono);
--text-mono-data:  10px / 1.2 var(--font-mono);
```

### 1.4 Icon Catalog (25 Custom Icons)

All icons: 24×24px viewBox, 2px stroke width, `stroke-linecap="round"`, `stroke-linejoin="round"`, `fill="none"`, color inherits from `currentColor`.

| # | Name | Description | SVG Path Summary |
|---|------|-------------|------------------|
| 1 | `jack-in` | Audio plug entering port | `circle r=4 cx=12 cy=8`, `ellipse rx=5 ry=2`, `line 12,12 to 12,20`, arrowhead |
| 2 | `jack-out` | Audio plug exiting port | Mirror of jack-in |
| 3 | `knob` | Top-view rotary knob | 2 concentric circles `r=10,6`, indicator line, 4 tick marks |
| 4 | `wave-sine` | Smooth sine wave | `C6 4, 8 4, 12 14 C16 24, 18 24, 22 14` |
| 5 | `wave-square` | Square wave | Sharp vertical transitions: `L6 18 L6 8 L10 8...` |
| 6 | `wave-saw` | Sawtooth wave | Diagonal ramp + vertical drop |
| 7 | `patch-cable` | Curved patching cable | Bézier curve + plug shapes at ends |
| 8 | `module` | Eurorack faceplate | Rectangle + screws + 2 knobs + 2 jacks |
| 9 | `rack` | 3U equipment rack | 3 sections with ventilation lines + screws |
| 10 | `led-on` | Illuminated LED | Small circle + 8 radial rays |
| 11 | `led-off` | Unlit LED | Small circle outline only |
| 12 | `spectrum` | Frequency bars | 8 vertical bars increasing in height |
| 13 | `oscilloscope` | Scope with trace | Rect + grid + sine wave path |
| 14 | `amplifier` | Triangle op-amp | Triangle + input/output lines + power rails |
| 15 | `filter` | Low-pass curve | Passband line + diagonal cutoff + knob marks |
| 16 | `mixer` | Mixing console | 4 channel faders |
| 17 | `power` | Power symbol | Circle + vertical line breaking out top |
| 18 | `signal-path` | Signal flow arrow | Arrow → module rect → arrow |
| 19 | `patch-bay` | I/O panel | Rect with 2 rows of 4 jacks |
| 20 | `frequency` | Hz dial | Semi-circle scale + needle |
| 21 | `envelope` | ADSR shape | Attack rise, decay fall, sustain, release |
| 22 | `lfo` | Slow sine + arrow | Wide sine + clockwise circular arrow |
| 23 | `midi` | 5-pin DIN | Circle + 5 inner dots + line |
| 24 | `clock` | Tempo indicator | Circle + hands + square wave |
| 25 | `attenuator` | Level adjust | Circle + vertical line + up/down arrows |

### 1.5 Spacing System — 8px Baseline Grid

| Token | PX | REM | Usage |
|-------|-----|-----|-------|
| `--space-0_5` | 4px | 0.25rem | Icon-text gap, LED-label gap |
| `--space-1` | 8px | 0.5rem | Knob spacing, grid snap, button gap |
| `--space-2` | 16px | 1rem | Module gutter, jack spacing, input padding |
| `--space-3` | 24px | 1.5rem | Module padding, rack gap, knob-to-edge |
| `--space-4` | 32px | 2rem | Rail padding, drawer inset |
| `--space-5` | 48px | 3rem | Module gap, rack row spacing |
| `--space-6` | 64px | 4rem | Section margin, modal inset |
| `--space-7` | 96px | 6rem | Content area padding |
| `--space-8` | 128px | 8rem | Hero spacing |

### 1.6 Border & Depth Treatments

| Context | Border | Radius | Chamfer |
|---------|--------|--------|---------|
| Module default | 1px solid `#2A2A2E` | 2px | clip-path(2px corners) |
| Module selected | 2px solid `--brass` | 2px | Same clip-path |
| Knob default | 1.5px solid `--text-muted` | 50% | — |
| Knob active | 1.5px solid `--brass` | 50% | — |
| Jack idle | 1.5px solid `#2A2A2E` | 50% | — |
| Input default | 1px solid `#2A2A2E` | 2px | — |
| Input focus | 1.5px solid `--brass` | 2px | — |

**Depth**: No `box-shadow` with blur. Depth via `translateY(-2px)` (hover) or `translateY(-4px)` (dragged). Hard drop shadow: `0 2px 0 0 rgba(0,0,0,0.5)`.

**Chamfer clip-path**:
```css
clip-path: polygon(2px 0, calc(100% - 2px) 0, 100% 2px, 
                   100% calc(100% - 2px), calc(100% - 2px) 100%, 
                   2px 100%, 0 calc(100% - 2px), 0 2px);
```

### 1.7 Component State Library

#### Module
| State | Visual |
|-------|--------|
| Default | bg: `--surface`, border: 1px solid `#2A2A2E` |
| Hover | bg: `--surface-hover`, border: 1px solid `#4A4A50`, translateY(-2px) |
| Selected | border: 2px solid `--brass` |
| Dragging | bg: `--surface-hover`, border: 1px solid `--brass`, translateY(-4px), opacity 0.85 |
| Disabled | opacity 0.5, pointer-events none |

#### Knob
| State | Visual |
|-------|--------|
| Default | border: 1.5px solid `--text-muted`, indicator hidden |
| Hover | border: 1.5px solid `--brass`, knurl opacity 0.3 |
| Active | border: 1.5px solid `--brass`, indicator visible, knurl 0.5 |
| At-limit | vibrate: 3px oscillation, 4 cycles, 100ms |
| Disabled | opacity 0.4, pointer-events none |

#### Cable
| State | Visual |
|-------|--------|
| Connected | 2.5px solid `--brass`, 0.5px highlight |
| Hover | 3px solid `--cable-hover` |
| Selected | endpoint offset rings (1px, r=14px) |
| Error | flash `--danger` 300ms × 3 |
| Dragging | 2.5px solid `--brass`, elastic lag |

#### Jack
| State | Visual |
|-------|--------|
| Idle | bg: `#16161A`, border: 1.5px solid `#2A2A2E`, 10px |
| Hover | border: 2px solid `--brass`, pulse on enter |
| Connected | bg: `--brass`, border: 1.5px solid `--brass` |
| Target (drag) | expanded ring: 14px, border `--brass`, pulse animation |

#### LED
| State | Visual |
|-------|--------|
| Off | `#1A1A1A`, static |
| Normal | `--teal`, pulse scale 1→1.2, 2s cycle |
| Attention | `--brass`, pulse scale 1→1.3, 1s cycle |
| Alert | `--danger`, 200ms on/off × 3, then 3s pause |
| Error | `--danger`, solid, no animation |

#### Button (Text Style)
| State | Visual |
|-------|--------|
| Default | color: `--brass`, bg: transparent, border: transparent |
| Hover | color: `--brass-light`, border: 1px solid `rgba(212,168,67,0.3)` |
| Pressed | bg: `--surface-active`, translateY(1px) |
| Disabled | color: `--text-disabled`, opacity 0.5 |

#### Input (Signal Groove)
| State | Visual |
|-------|--------|
| Default | bg: `--surface-input`, border: 1px solid `#2A2A2E` |
| Focus | border: 1.5px solid `--brass` |
| Error | border: 1.5px solid `--danger` |
| Disabled | opacity 0.4 |

### 1.8 Complete CSS Custom Properties (`:root`)

```css
:root {
  /* Colors: Root & Surface */
  --bg-root: #0B0B0D;
  --surface: #16161A;
  --surface-hover: #1E1E22;
  --surface-active: #222228;
  --surface-elevated: #1A1A1E;
  --surface-input: #131317;

  /* Colors: Accents */
  --brass: #D4A843;
  --brass-dim: #A58736;
  --brass-light: #E8C56E;
  --teal: #3D5A5C;
  --teal-bright: #4F7A7D;
  --teal-dim: #2E4446;

  /* Colors: Signals */
  --success: #6A8A5C;
  --success-bright: #7EA66E;
  --danger: #C8553D;
  --danger-bright: #E06A50;
  --warning: #C8943D;

  /* Colors: Text */
  --text-primary: #F5F0E7;
  --text-secondary: #C4BFB4;
  --text-muted: #8A8882;
  --text-disabled: #5A5854;
  --text-on-brass: #0B0B0D;

  /* Colors: Borders */
  --border-subtle: #2A2A2E;
  --border-brass: #D4A843;
  --border-error: #C8553D;
  --border-success: #6A8A5C;
  --border-hover: #4A4A50;

  /* Colors: Knob */
  --knob-body: #16161A;
  --knob-indicator: #D4A843;
  --knob-rim: #2A2A2E;

  /* Colors: LED */
  --led-off: #1A1A1A;
  --led-idle: #3D5A5C;
  --led-normal: #D4A843;
  --led-urgent: #C8553D;

  /* Colors: Jack */
  --jack-idle: #16161A;
  --jack-rim: #2A2A2E;
  --jack-connected: #D4A843;

  /* Colors: Cable */
  --cable-default: #D4A843;
  --cable-hover: #E8C56E;
  --cable-error: #C8553D;

  /* Typography */
  --font-heading: 'IBM Plex Sans', 'IBM Plex Sans Arabic', sans-serif;
  --font-body: 'Tajawal', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --fw-heading: 600;
  --fw-body: 400;
  --fw-mono: 400;
  --lh-tight: 1.1;
  --lh-normal: 1.4;
  --lh-mono: 1.2;
  --ls-heading-xl: -0.02em;
  --ls-heading-lg: -0.01em;
  --ls-label: 0.02em;
  --ls-uppercase: 0.08em;

  /* Spacing */
  --space-0_5: 4px;
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 48px;
  --space-6: 64px;
  --space-7: 96px;
  --space-8: 128px;

  /* Semantic spacing */
  --module-gap-h: var(--space-5);
  --module-gap-v: var(--space-4);
  --rail-padding-h: var(--space-4);
  --grid-snap: var(--space-1);
  --grid-unit: 40px;
  --rail-height: 56px;

  /* Borders */
  --border-width-default: 1px;
  --border-width-selected: 2px;
  --radius-default: 2px;
  --radius-full: 50%;
  --chamfer-size: 2px;

  /* Timing */
  --micro: 100ms;
  --normal: 300ms;
  --macro: 400ms;
  --snap: 150ms;

  /* Easing */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.76, 0, 0.24, 1);
  --ease-bounce: cubic-bezier(0.34, 1.5, 0.64, 1);
}
```

---

## 2. Global Layout & Navigation

### 2.1 Base DOM Hierarchy

```
<body style="background: var(--bg-root); margin: 0; font-family: Tajawal;">
  <div id="app">
    <header id="command-rail">          <!-- Top Rail, fixed, z-index 1000 -->
      <div class="rail-logo"></div>     <!-- 36px SVG wave+jack icon -->
      <nav class="rail-nav-knobs">      <!-- 4 section knobs -->
        <div class="knob" data-section="library"></div>
        <div class="knob" data-section="paths"></div>
        <div class="knob" data-section="tests"></div>
        <div class="knob" data-section="statistics"></div>
      </nav>
      <div class="rail-user"></div>     <!-- 36px wave ring avatar -->
    </header>
    <div id="user-drawer" class="hidden"></div>  <!-- 360px, slides from top -->
    <main id="workspace">               <!-- z-index 10 -->
      <div class="dot-grid-bg"></div>   <!-- 1px dots at 40px intervals -->
      <div class="module-container"></div>
    </main>
    <footer id="bottom-tool-case" class="md:hidden"></footer>  <!-- mobile only -->
  </div>
</body>
```

### 2.2 Z-Index Stack

| Layer | Element | Z-Index |
|-------|---------|---------|
| Background | dot-grid-bg | 0 |
| Content | module-container | 10 |
| Transition | wipe-overlay | 500 |
| Drawer | user-drawer | 999 |
| Rail | command-rail | 1000 |
| Tooltip | knob-tooltip | 1100 |

### 2.3 Top Command Rail

- Fixed position, full width, height 56px, background `--surface`
- Bottom border: 1px solid `--brass`
- Padding: 0 16px horizontal, flex layout with align-items center
- Gap between item groups: 8px
- Layout: [Logo] [flex-start] [Nav Knobs] [flex-end] [User Module]

### 2.4 Logo

- 36px SVG icon — a sine wave merging into a circular patch jack
- No text, no wordmark
- Click: returns workspace to default/Library view
- Hover: rail border-bottom transitions to `--brass-light` (`#E0B84C`)
- `aria-label="Return to library home"`

```
<svg viewBox="0 0 36 36">
  <path d="M2 26 C 2 10, 9 10, 9 10 C 9 10, 14 10, 18 18 C 22 26, 27 26, 27 26"
        fill="none" stroke="#D4A843" stroke-width="2" stroke-linecap="round"/>
  <circle cx="27" cy="26" r="4" fill="#0B0B0D" stroke="#D4A843" stroke-width="1.5"/>
</svg>
```

### 2.5 Navigation Knobs

- 4 circular knobs: [Library] [Paths] [Tests] [Statistics]
- 40px diameter, `border-radius: 50%`, bg `--surface`, border 1.5px solid `--text-muted`
- Knurled edge: `repeating-conic-gradient(#5A5854 0deg 1.5deg, transparent 1.5deg 36deg)`
- Indicator line: SVG `line` 2px×8px, `--brass`, rotate controlled by JS
- Label: 10px Tajawal, below knob, color `--text-muted`
- **States**: idle (muted border, indicator hidden), hover (brass border, knurl 0.3), active (brass border, indicator rotates 15°, knurl 0.5), focused (brass border + 1px dotted ring), disabled (opacity 0.4)
- **Interaction**: click to activate, vertical drag (1px = 0.5°), scroll wheel (1 tick = 5°)
- **Tooltip**: "Library · 1/4" appears above knob during interaction, fades 500ms after stop
- **Section change**: horizontal wipe transition (300ms ease-out), `history.pushState`, `popstate` handling

### 2.6 User Module & Drawer

- 36px SVG wave ring + 32px avatar circle
- Wave ring: `--teal` trace pulses (CSS animation 2s cycle)
- Click opens User Drawer (360px, slides down from rail with 250ms ease-out)
- Drawer content: Avatar + name + email, divider, 4 nav links (Settings with gear icon, Notifications with bell+LED, Theme toggle as 20px mini knob, Logout with power icon)
- Theme knob: 20px, rotates 180° between dark/light
- Focus trap inside drawer when open. Close: click outside, Escape, or click avatar again.

### 2.7 Workspace (Patch Bay)

- `position: absolute; top: 56px; left: 0; right: 0; bottom: 0; overflow: auto`
- Background `--bg-root` with dot grid: `radial-gradient(circle, #1F1F23 1px, transparent 1px)` at 40px intervals
- Module container: `position: relative; z-index: 10`
- Modules snap to 40px grid (`Math.round(position / 40) * 40`)
- Racks: modules can stack in horizontal rows with 24px vertical gap

### 2.8 Event Bus

| Event | Detail | Dispatched By |
|-------|--------|---------------|
| `section:change` | `{ section, from }` | Knob click, Logo click |
| `drawer:open/close` | `{}` | Avatar click |
| `theme:toggle` | `{ theme }` | Drawer toggle |
| `patch:connect/disconnect` | `{ sourceId, targetId }` | Cable interaction |
| `knob:value-change` | `{ knobId, value, rotation }` | Knob rotation |
| `module:drag-start/move/end` | `{ id, x, y }` | Module drag |
| `workspace:resize` | `{ width, height }` | Window resize |

### 2.9 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `1`-`4` | Switch to Library/Paths/Tests/Statistics |
| `Escape` | Close drawer / cancel drag |
| `Ctrl+Z` | Undo last cable connection |
| `Tab` | Cycle focus through rail items |

---

## 3. Learner Experience

### 3.1 Signal Path Module

A horizontal row of connected modules representing learning path stages. Flexbox with 8px gap, centered, horizontal overflow scroll.

#### Collapsed Module (260×180px)
| Element | Spec |
|---------|------|
| Width | 260px |
| Height | 180px |
| Background | `--surface` |
| Border | 1px solid `#2A2A2E`, chamfered |
| Header strip | 4px tall, full width, colored by state |
| Genre icon | 28×28px SVG |
| Title | 14px, medium weight, 1-line truncate |
| Wave indicator | 12px height SVG at bottom, varies by state |
| Jacks | 10px circles at left (input) and right (output) edges |

#### Module States
| State | Border | Header | Wave | Interaction |
|-------|--------|--------|------|-------------|
| Locked | 1px dashed `#2A2A2E` | `#2A2A2E` | Flat line `#2A2A2E` | cursor not-allowed |
| Available | 1px solid `#2A2A2E` | `--text-muted` | Flat line `--text-muted` | click expands |
| Active | 2px solid `--brass` | `--brass` | Pulsing sine A=3px, λ=60px | click expands |
| Completed | 1px solid `--success` | `--success` | Steady sine A=6px, `--success` | click re-opens |

#### Cable Connections (Between Modules)
- SVG Bézier path: `M x1,y1 C cp1x,cp1y cp2x,cp2y x2,y2`
- Control point offset: `dx * 0.4` from each endpoint
- Cable states: completed (2px `--success` solid), active (2px `--brass` with pulse 2s), upcoming (1px dashed `--text-muted`)

#### Inline Expand (300ms ease-out)
- Click unlocked module → expands to 600×400px
- Width/height transition + clip-path
- Expanded content: video embed placeholder (320×180), content text, exercise list with radio dots, Finish knob (40px, rotation 0→135° marks complete)
- Close via X icon top-right or clicking header area (300ms ease-in collapse)

### 3.2 Overall Progress Indicator

- Full-width, 12px height, background `#1F1F23`, border 1px `#2A2A2E`
- SVG waveform: sine wave progression from left (0%) to right (100%)
- Color gradient: 0-50% `--teal` → 50-100% interpolates to `--brass`
- At 100%: transitions to `--success`, celebratory 3-pulse scale animation
- Breathing idle animation: `scaleY` 1→0.85→1 over 4s

### 3.3 Oscillator Test Interface

Full-screen modal overlay within workspace, `z-index: 50`.

#### Central Module
- 80% width (max 960px), height 500px, `--surface`, chamfered
- Layout: Test Name (14px brass, top-left), Spiral Timer (40px, top-right), Waveform Display (70% width, 160px high), 4 Answer Knobs, Patch Answer button, Progress Counter

#### Spiral Timer
- SVG spiral, 40px, 2.5 turns, total length ~283px
- Unwinds via `stroke-dashoffset`: from 0 to totalLength over test duration
- Color: `--brass` normally, `--danger` with pulse when <25% time remains
- At 0: test auto-submits

#### Answer Selection — 4 Knobs
- 32px diameter each, labeled A/B/C/D with answer text below
- Click rotates knob 45°, border turns `--brass`, radio behavior
- Submit via "Patch Answer" text button (brass, text-only, hover underline)

#### Wave Feedback
- **Correct**: wave transitions to stable `--success` sine, upward sweep 300ms, cables pulse
- **Wrong**: wave distorts jagged `--danger` 400ms, wrong knob jiggles (±5°, 200ms)
- **Timeout**: wave flattens to line, "Signal Lost" in `--danger`

#### Score Display
- "Frequency: 8/10 · 80%" in 20px `--brass`, `font-variant-numeric: tabular-nums`
- "Return to Path" text button closes oscillator (200ms fade)

### 3.4 Path Completion

- All cables pulse synchronously: opacity 0.7→1, 3 cycles, `--brass`→`--success`
- Progress wave reaches 100%, triple pulse celebration
- "Path Patched" badge: bordered text `--success`, scale-in animation 300ms

---

## 4. Manager Studio

### 4.1 Amplifier Rack (Group Display)

- 400×280px module, `--surface`, chamfered
- Header: VU meter (100×8px, 10 segments, teal→success→brass), group name (14px brass), learner count [12]
- Content area: flexbox row-wrap of Learner Bank modules

### 4.2 Learner Bank (120×80px)

- Name (10px trunctated), avatar (20px circle), vertical VU meter (6×40px)
- VU meter fill: 0-33% `--danger`, 34-66% `--teal`, 67-100% `--success`
- 3 scale marks at 25%/50%/75%
- Output jack (right, 8px, drag source) and input jack (left, 8px, drop target)

### 4.3 Cable Patching (Enrollment)

- Click output jack → drag cable (2px `--brass` Bézier) → drop on path input jack
- Valid target: jack expands to 12px, border `--brass`
- Connect: modules flash (300ms), enrollment API fires
- Disconnect: double-click cable → X icon at midpoint → click → particle disintegration (300ms)
- Multi-learner bundling: shared trunk (3px) → branches (1.5px) to each learner

### 4.4 Activity Oscilloscope

- Double-click learner → expands to 600×350px scope
- 500×220px trace area with grid, `--brass` line drawing left→right over 500ms
- Crosshair hover: tooltip "Day 14 · 3.2h · Test: 85%"
- Scroll wheel: 7d → 30d → 90d time range
- Control knobs (24px): Time Range, Refresh (spins 360°), Export (PNG snapshot)

### 4.5 LED Notifications

- 6px dot on learner module corners
- States: Off (`#1A1A1A`, 7+ days idle), Normal (`--teal`, 2s pulse), Achievement (`--brass`, 0.5s pulse), Urgent (`--danger`, 3 quick blinks + 3s pause)
- Group summary LED (10px) in amplifier header

---

## 5. Admin Central Laboratory

### 5.1 Global Module Bank

- Floating panel, 300×500px, triggered by "Library" button top-left of workspace
- Tabs: [Courses] [Tests] [Certificates] [Users] [Roles]
- Each tab shows draggable module cards (80×80px) with output jack
- Drag card → clone into workspace (original remains in library)

### 5.2 Patch Builder (Learning Path Creator)

- Drag empty Path module (800×200px) from library → workspace
- Drag content modules inside → auto-align horizontally (200×120px each, 16px gap)
- Patch connections: click output jack → drag cable → drop on input jack
- Cable solid `--brass` 2px with pulse animation (1.5s). Click to select, double-click to delete (particle disintegration)
- Click cable → threshold popup (200×100px) with 32px knob for pass percentage
- Label "≥70%" appears below cable midpoint in `--teal`

### 5.3 Wave Shaper (Test Editor)

- 400px height waveform canvas, full workspace width
- Questions = wave nodes (48px circles, `--surface`, 1.5px `--brass` border)
- Connected by horizontal `--teal` line (1.5px)
- Y-position of node = difficulty (higher Y = easier)
- Drag nodes horizontally (snaps to 80px grid) or vertically (free)
- Click node → properties panel (280px, right side) with synth-style controls:
  - Question text: "Signal Input Groove" (recessed strip, 32px height)
  - Type knob (24px): Multiple Choice / True-False / Essay
  - Options: 4 stacked grooves for answers
  - Score knob (24px, 0-100), Time Limit knob (24px, 0-300s)
- Right-click node → "Add Branch" → dashed `--brass` line to target node → condition label

### 5.4 Spectrum Analyzer

- Full-width, 400px height grid heatmap
- X-axis: time, Y-axis: skills/courses/users (filter-dependent)
- Cell colors (solid): `--bg-root` (none) → `#1A2A2B` (low) → `#2D4F50` (med) → `#7A6B30` (high) → `--success` (complete)
- Left column 48px: 4 control knobs (32px) — Date Range (7d/30d/90d/1y), Department, Metric Type (Activity/Scores/Completion/Time), Resolution (Daily/Weekly/Monthly)
- Zoom knob (24px): 1x/2x/4x, bottom-right

---

## 6. Micro-Interaction & Physics System

### 6.1 Cable Physics

- **Rendering**: SVG Bézier path, 2.5px solid `--brass`, 0.5px highlight offset 1px left
- **Bézier formula**: `P0` = output jack center, `P3` = input jack center, `cp1.x = x1 + dx*0.4`, `cp2.x = x2 - dx*0.4`
- **Drag**: `requestAnimationFrame` at 60fps, elastic lag (tension 0.4, friction 0.2)
- **Valid target detection**: iterate input jacks, if `distance <= 15px` jack is "hot" (expands to 14px, border `--brass`)
- **Invalid drop**: cable dissolves — 8 marker points fade sequentially tip→base over 200ms
- **Valid drop**: cable snaps to jack center, jacks settle (expand to 12px for 150ms, return to 10px)
- **Disconnect**: double-click → X icon at midpoint (`--danger`, 16px) → particle scatter (6-8 dots, 400ms)
- **Module move**: all connected cables recalculate via rAF at 60fps
- **Auto-break**: module out of bounds > 2000ms or rapid > 500px in 100ms

### 6.2 Knob Behavior

- **4 sizes**: 56px (stats), 40px (nav/primary), 24px (fine-tuning), 16px (inline)
- **Construction**: `border-radius: 50%`, knurled via `repeating-conic-gradient`, indicator SVG line, center dot 3px
- **Rotation**: vertical drag (1px = 0.5°), scroll wheel (1 tick = 5°), range -135° to +135° (270° total)
- **At-limit vibration**: 3px horizontal oscillation, 4 cycles, 100ms total
- **Detents** (enum knobs): 50ms scale snap on boundary crossing
- **Tooltip**: JetBrains Mono 11px, above knob, fades 500ms after last interaction

### 6.3 Module Dragging

- **Drag handle**: top 8px strip, full width
  - Default: `--surface`, hover: `--brass`, active: `--brass` + darker bottom border
- **Drag mechanics**: lift 2px (translateY), dim others to opacity 0.95
- **Grid snap**: `Math.round(newX / 40) * 40`, 150ms ease-out + 2px bounce overshoot (50ms)
- **Rack detection**: if module center inside rack boundary, auto-align to nearest flex slot
- **Invalid drop** (outside workspace): animate back to original position over 200ms

### 6.4 LED Notifications

- 8px circle, 1px border, solid color (no glow/blur)
- Normal: `--teal`, scale 1→1.2→1, 2s cycle
- Attention: `--brass`, scale 1→1.3→1, 1s cycle
- Alert: `--danger`, 200ms on/off × 3, 3s pause, JS-driven
- Error: `--danger`, solid, no animation

### 6.5 Motion Design

| Interaction | Duration | Easing |
|-------------|----------|--------|
| Micro (hover, focus) | 100ms | `ease-out` |
| Normal (expand, drawer) | 300ms | `cubic-bezier(0.16, 1, 0.3, 1)` |
| Macro (section wipe) | 400ms | `ease-in-out` |
| Celebration | 600ms | `ease-out` |
| Snap/bounce | 150ms | `ease-out` + 2px overshoot |

- **Wave breathing**: every wave at rest oscillates ±2% amplitude at 0.5Hz, staggered phase offsets
- **No `transition: all`** — always specify explicit properties
- **Transform-based** for GPU acceleration (translate, scale, rotate) over layout properties

---

## 7. Responsive Design

### 7.1 Breakpoints

| Range | Name | Rail | Workspace | Knobs | Grid |
|-------|------|------|-----------|-------|------|
| ≥1440px | Desktop XL | Full 56px | Free-form X+Y | 40px labeled | 40px dots |
| 1024-1439px | Desktop | Full 56px | Free-form X+Y | 36px labeled | 32px dots |
| 768-1023px | Tablet | Compact 48px | Y-only, full-width racks | 32px icon-only | 24px dots |
| <768px | Phone | Hidden (bottom bar) | Y-only, single column | 24px in bottom bar | None |

### 7.2 Bottom Tool Case (Phone)

- Fixed bottom, 64px height, `--surface`, top border 1px `--brass`
- 5 icon buttons evenly distributed: Library, Paths, Create (36px patch jack), Tests, User
- Active icon: `--brass` stroke, inactive: `--text-muted`
- Center Create button: opens floating menu (140px, `--surface`, 1px `--brass`) with [New Path] [New Test] [New Module]
- Safe area inset-bottom: 20px for notched phones

### 7.3 Phone Adaptations

- **Learning paths**: vertical list of cards with vertical cable line (2px `--brass`) down left edge
- **Jacks**: input top-left, output bottom-left of each card
- **Patching method 1**: sequential tapping — tap output jack → preview line (1.5px dashed) → tap input jack → connection
- **Patching method 2**: long-press (500ms) → floating menu of nearby modules with input jacks
- **Spectrogram**: 14px cells (instead of 20px), 4 control knobs horizontal below, pinch-to-zoom replaces zoom knob

### 7.4 Touch Targets

| Element | Visible | Hit Area |
|---------|---------|----------|
| Knob | 24-40px | 48×48px |
| Jack | 10px | 44×44px |
| Icon button | 28px | 48×48px |
| Cable | 2px | 20px wide invisible path |

### 7.5 Cross-Breakpoint Transitions

- On resize: modules reflow LTR→rack layout, cables recalculate (debounced 150ms)
- Active patch sessions cancelled on breakpoint crossing (toast notification)
- Phone orientation change: bottom bar collapses to 56px height, spectrogram height adjusts

---

## 8. Integration Audit & Completeness

### 8.1 Login / Signup — "Signal Tuning Screen"

Full-screen, `--bg-root` with dot grid. Center module 480×400px, `--surface`, chamfered.

- **Username field**: "Signal Input Groove" — 40px tall recessed strip, `#0B0B0D` bg, 1px `#2A2A2E` border, cursor blinks
- **Password field**: same groove with caps lock LED indicator (6px)
- **Login action**: "Patch In" jack icon (32px, `--brass` border) with text "Patch In"
  - Click → cable animation shoots from jack to "System Module" icon
  - Success: cable stabilizes, wave sweeps across, transition to workspace (500ms)
  - Failure: cable jitters, "Signal Noise — Check Credentials" (`--danger`, 12px)
- **Signup toggle**: "No module? Register" → swaps to registration (email, name, confirm grooves)
- **Forgot password**: "Signal Lost?" → single email groove → "Reset signal sent"

### 8.2 User Profile — "Identity Module"

- 500×400px module, `--surface`, chamfered, opens in workspace
- Header: "Module ID: USR-42A7" + "Manufacture Date: 2024-01-15" (JetBrains Mono 12px muted)
- 3 mini oscilloscope traces (160×40px each): XP cumulative (`--brass`), Tests completed step wave (`--teal`), Streak pulse (`--success`)
- Badges as jack plug labels: "Python Master", "Math Wiz"
- Edit controls: 3 small knobs (20px) for Name, Email, Location

### 8.3 Notifications — "Pulse Monitor"

- 360×500px module, opens from top-right of workspace
- Each notification = a "pulse": icon + title (12px) + description (10px) + time (8px mono)
- Unread: left border 2px `--brass`, LED dot visible
- Read: transparent left border, no dot
- Empty: "No incoming signals" with flat line wave icon

### 8.4 Empty & Error States

| Context | Message | Visual |
|---------|---------|--------|
| Empty Library | "No modules loaded — Drag a module from the library to start" | Empty patch bay with faint cable outline |
| Empty Paths | "No paths patched" | Single unconnected jack icon |
| Empty Tests | "No oscillators configured" | Flat wave line |
| Empty Statistics | "No signal data" | Faint grid only |
| 404 | "Signal Lost — Carrier Wave Not Found" | Wave splitting into dashes, fading rightward |
| 500 | "System Noise — Unexpected Interference" | Jagged distorted wave `--danger` |
| Loading | Oscilloscope sweep trace (6px dot L→R) + "Establishing Signal..." | 80×40px module |

### 8.5 Search — "Signal Input Strip"

- Full-width, 32px height, `--surface`, 1px `#2A2A2E` border
- Left: frequency indicator (20px knob icon, static)
- Center: input groove — type in JetBrains Mono 12px
- Right: 3 filter knobs (20px) — Type, Status, Date
- Results as "responsive wavelets": 16px wave icons with labels, horizontal flex-wrap

### 8.6 Metaphor Purity — Term Replacements

| Banished Term | Replacement | Files to Update |
|---------------|-------------|-----------------|
| Login | Signal Tuning | `(auth)/login/page.tsx` |
| Register | Module Registration | `(auth)/register/page.tsx` |
| Forgot Password | Signal Lost | `(auth)/forgot-password/page.tsx` |
| Profile | Identity Module | `profile/page.tsx` |
| Notifications | Pulse Monitor | `DashboardShell.tsx` |
| Settings | Module Config | `admin/settings/page.tsx` |
| Dashboard | Workspace / Patch Bay | `dashboard/page.tsx` |
| Sidebar | Command Rail | `DashboardShell.tsx` |
| Login button | Patch In jack | All auth forms |
| Logout | Disconnect | `Header.tsx` |
| Save | Patch / Commit | All forms |
| Delete | Cut Cable / Remove Module | Admin pages |
| Loading spinner | Oscilloscope trace | `SkeletonLoading.tsx` |
| Table/Card | Signal level / Module | Admin CRUD |
| Form | Control panel / Groove | All forms |
| Button | Knob / Jack / Toggle LED | All buttons |
| Progress bar | VU meter / Progress wave | `progress.tsx` |
| Tabs | Knob selector | `tabs.tsx` |
| Card | Module | `card.tsx` |
| Input | Signal groove | `input.tsx` |
| Checkbox | Toggle LED | Checkbox usage |
| Search bar | Signal Input Strip | `DashboardShell.tsx` |
| Breadcrumb | Signal path | `Header.tsx` |
| "Sign In" | "Patch In" | All auth text |
| "Sign Out" | "Disconnect" | User menu |
| "Create account" | "Register Module" | Auth |
| "Loading" | "Establishing Signal..." | Skeleton |
| "Error" | "System Noise" | Error pages |
| "Success" | "Signal Locked" | Feedback |
| "Empty" | "No Signal" | Empty states |
| "Edit" | "Tune / Adjust Frequency" | Controls |
| "Submit" | "Patch Answer" | Tests |
| "Complete" | "Module Patched" | Paths |

### 8.7 User Flow Maps

#### Learner Flow
1. **Signal Tuning** → login → workspace (Library view)
2. Turn **Paths** knob → wipe → Signal Path modules + Progress Wave
3. Click module → inline expand → view content
4. Click "Take Test" → Oscillator overlay → answer via knobs → Patch Answer → wave feedback
5. Complete all modules → cable pulse celebration → "Path Patched" badge
6. Turn **Statistics** knob → spectrogram + progress wave

#### Manager Flow
1. Login → Manager Studio (Amplifier Racks + Learner Banks)
2. Monitor LEDs → investigate urgent via double-click → oscilloscope
3. Patch learner to path: drag cable from learner output to path input
4. Add group via right handle

#### Admin Flow
1. Login → Library view with admin permissions
2. Open Library drawer → browse/create content modules
3. Open Patch Builder → drag path module → populate → patch → set thresholds
4. Open Wave Shaper → edit test nodes → set branching → save
5. Spectrum Analyzer → turn knobs → observe patterns

### 8.8 Final Component Inventory

| # | Component | Properties | States | Used By |
|---|-----------|-----------|--------|---------|
| 1 | **Module** | `width`, `height`, `state`, `position`, `chamfer`, `draggable` | idle, hover, selected, dragging, disabled, expanded, locked | All agents |
| 2 | **Knob** | `diameter` (16/24/32/40/56), `value`, `range`, `step`, `rotation`, `label` | default, hover, active, at-limit, disabled, focus | All agents |
| 3 | **Cable** | `from`, `to`, `state`, `color`, `width`, `dash`, `bezier` | connected, hover, selected, error, dragging, upcoming | A2, A3, A4 |
| 4 | **Jack** | `type` (in/out), `diameter` (8/10), `position`, `state`, `innerFill` | idle, hover, connected, target, drag-source | A2, A3, A4 |
| 5 | **LED** | `color`, `animation`, `size` (6/8/10) | off, normal, attention, alert, error | A3, A8 |
| 6 | **VU Meter** | `orientation`, `segments`, `value`, `segmentColors`, `scaleMarks` | idle, transitioning, empty, overload | A3, A8 |
| 7 | **Oscilloscope** | `data`, `range`, `grid`, `trace`, `crosshair` | rendering, interactive, zooming, empty | A3, A8 |
| 8 | **Spectrum Cell** | `x`, `y`, `intensity`, `color` | cold, warm, hot, empty | A4 |
| 9 | **Wave Indicator** | `width`, `height`, `state`, `amplitude`, `period`, `stroke` | locked, available, active, completed | A2 |
| 10 | **Patch Bay (Workspace)** | `scroll`, `grid`, `modules` | default, transitioning, mobile | A1 |
| 11 | **Command Rail** | `height`, `items`, `z-index` | default, logo-hover, mobile | A1 |
| 12 | **Bottom Tool Case** | `icons`, `createBtn` | default, active | A1, A7 |
| 13 | **Signal Input Strip** | `query`, `results`, `filters`, `empty` | idle, focused, has-results, no-results | A8 |
| 14 | **Signal Groove** | `type`, `placeholder`, `value`, `disabled`, `caps` | idle, focused, filled, error | A8 |
| 15 | **User Drawer** | `open`, `width`, `links`, `theme` | closed, open | A1 |
| 16 | **Pulse Entry** | `type`, `title`, `description`, `time`, `unread` | unread, read | A8 |
| 17 | **Search Wavelet** | `label`, `type`, `active` | default, hover, active | A8 |
| 18 | **Threshold Popup** | `knob`, `value`, `options` | visible, hidden | A4 |
| 19 | **Disconnect Icon** | `position`, `color` | default, hover | A3, A5 |
| 20 | **Path Module** | `title`, `state`, `genre`, `wave`, `jacks`, `content`, `finishKnob` | locked, available, active, completed, expanded | A2 |
| 21 | **Oscillator Screen** | `questions`, `currentIndex`, `timeRemaining`, `answerKnobs` | open, closed, correct, wrong, timeout | A2 |
| 22 | **Spiral Timer** | `totalTime`, `remaining`, `diameter`, `turns` | running, urgent, expired | A2 |
| 23 | **Amplifier Module** | `name`, `learnerCount`, `progress`, `learners` | normal, active, empty, drag-target | A3 |
| 24 | **Signal Level Meter** | `value`, `orientation`, `scaleMarks` | 0-33%, 34-66%, 67-100% | A3 |
| 25 | **Wave Node** | `id`, `question`, `type`, `branches`, `position` | idle, selected, connected, drag | A4 |
| 26 | **Patch Builder** | `path`, `modules`, `connections`, `thresholds` | empty, editing, connected | A4 |
| 27 | **Wave Shaper** | `nodes`, `branches`, `canvas` | editing | A4 |
| 28 | **Spectrum Analyzer** | `knobs`, `cells`, `zoom`, `tooltip` | rendering, interactive, empty, loading | A4 |
| 29 | **Identity Module** | `avatar`, `traces`, `badges`, `editKnobs` | default, editing | A8 |

---

*End of SkillSynth Modular Synthesizer Design System — Complete Specification*
