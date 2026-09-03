# SkillSynth Promo Video

## What this is

`skillsynth-promo.mp4` is the SkillSynth product promo: a 60-second, 1920x1080@30 H.264 (High, yuv420p) clip with AAC 48 kHz stereo audio (faststart, 21.9 MB). It showcases the **real SkillSynth application** — the bilingual (AR/EN, RTL-first) student frontend and the admin app — dressed in the Warm Craft brand. It is not a mockup; every screen was captured from the running app.

## How it was made

The final edit is assembled from three streams, then muxed once:

1. **Ken Burns body** — a stills edit of **13 distinct real app screens** (login, dashboard, wizard flow, catalog, category, skill detail, learn, analytics, and admin tools) plus **4 PIL title cards**, each given a slow zoom/pan (zoompan) and chained with **0.4 s crossfades**. Rendered to `work/clips/picture_only.mp4` (~60 s).
2. **Intro/outro bookends** — abstract texture clips that open and close the video.
3. **CC0 music bed** — trimmed to the cut at the mux stage.

The final **mux** trims the music to 60.03 s, applies **volume 0.6**, and a **5 s fade-out**, then encodes the whole thing down to `skillsynth-promo.mp4`.

### Bookends — honest note

The plan originally called for **AI text-to-video bookends** via inference.sh (`belt`, Veo). That could not run: the account had a **$0.00 balance** (a **$0.50 minimum** was required). The **pre-planned fallback** was used instead: programmatic **ffmpeg abstract texture clips** (`src` gradients + noise — paper/ochre tones for the 8 s intro, paper/sage for the 6 s outro). They live in `work/ai/`. **These bookends are NOT AI-generated.**

### Screens capture

Real screens were captured with **Playwright (Python) driving system Chromium headless** at 1920x1080:

- `scripts/capture.py` — primary surveys of the app
- `scripts/capture_interactions.py` — interactive states
- `scripts/capture_wizard.py` — the on-boarding wizard flow

*(The chrome-devtools MCP was unavailable — no Chrome was found at the expected path — so headless Playwright was used instead.)*

### Title cards

`scripts/make_cards.py` renders the 4 title cards with **pure PIL**, using the **real brand fonts** — Bricolage Grotesque, El Messiri, Public Sans, and Noto Sans Arabic — with **RTL shaping via libraqm**, the **Warm Craft palette**, and hairline rules. Outputs land in `work/frames/`.

### Music

"Waiting Around (LoFi, Calm)" by **HoliznaCC0** — **CC0 1.0 Universal Public Domain**, instrumental, **not AI-generated**. Attribution is recorded in `work/audio/attribution.txt`.

## Re-render

Regenerate the Ken Burns body from anywhere:

```
bash brand/video/scripts/render.sh
```

Then reconstruct the final file with the mux command:

```
ffmpeg -y -i brand/video/work/clips/picture_only.mp4 -i brand/video/work/audio/track.mp3 \
  -filter_complex "[1:a]aresample=48000,volume=0.6,afade=t=out:st=55:d=5[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -t 60.033 -movflags +faststart \
  brand/video/skillsynth-promo.mp4
```

## Verification

```
bash brand/video/scripts/verify.sh <path-to-mp4>
```

The script prints the spec table and builds a contact sheet. Expected spec: **1920x1080@30, yuv420p, AAC 48 kHz, ~60 s.**

## Music attribution

Held in `work/audio/attribution.txt` (track, artist, license, source links, and usage facts). CC0 is public domain so attribution is not required, but it is recorded for transparency.

## Brand guardrails

- **Warm Craft palette** (`palette.json`) — no gradients, no neon, no glassmorphism.
- **1 px hairlines**, tiny radii.
- **Mark 1:1 never recolored**, kept with 25% clear space.
- **Bilingual EN+AR** — English display type is primary; Arabic accents use **El Messiri** in **ochre-deep**.
- Arabic is **RTL and never capitalized**; English is **sentence case**.

## Files

```
brand/video/
├── skillsynth-promo.mp4          # final deliverable (1920x1080@30, 60.03s, 21.9 MB)
├── README.md                     # this file
├── scripts/
│   ├── capture.py                # Playwright screen capture (primary)
│   ├── capture_interactions.py   # Playwright interactive-state capture
│   ├── capture_wizard.py         # Playwright wizard capture
│   ├── make_cards.py             # PIL title-card rendering
│   ├── render.sh                 # Ken Burns edit + xfade -> picture_only.mp4
│   └── verify.sh                 # spec table + contact sheet
└── work/
    ├── frames/                   # 4 title cards (PIL)
    ├── screens/                  # ~33 captured app screens
    ├── ai/                       # bookend texture clips (intro.mp4, outro.mp4)
    ├── clips/                    # picture_only.mp4 + contact sheets
    └── audio/                    # track.mp3 + attribution.txt
```
