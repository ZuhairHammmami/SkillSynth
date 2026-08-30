# SkillSynth Promotional Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a ~60-second, 1080p30 promotional video (`brand/video/skillsynth-promo.mp4`) showcasing SkillSynth's real pages/features "in detail" under the Warm Craft brand, with an AI-generated abstract welcome/closing, a CC0/royalty-free music bed, and **bilingual English + Arabic** on-screen copy (English-first display with Arabic accents, per identity; no voiceover).

**Architecture:** Three content streams composited in ffmpeg: (1) AI text-to-video abstract textures (via `belt`/inference.sh, logged in) for intro/outro bookends; (2) real UI screenshots of the running app (captured via chrome-devtools tools, animated with Ken Burns pan/zoom in ffmpeg) as the body; (3) PIL-rendered brand title cards (mark + wordmark + bilingual copy in real brand fonts). All frames 1920x1080, Warm Craft palette (no gradients/neon/glass), then muxed with a CC0 music bed I source from the web.

**Tech Stack:** `belt` (inference.sh CLI, logged in) for AI textures; chrome-devtools MCP tools (navigate/screenshot) for UI capture; Pillow (PIL 12.3) for title cards; ffmpeg n9 for Ken Burns, transitions (xfade), and final H.264/AAC mux; brand fonts + `brand/identity/palette.json` colors.

**Spec:** Warm Craft brand — `brand/identity/guidelines.md`, `palette.json`, `typography.md`. AI video models — `.agents/skills/ai-video-generation/SKILL.md`.

## Global Constraints
- **Brand rules (guidelines.md):** no gradients, neon, glassmorphism, or drop-shadows under light text. Depth via 1px hairlines (`#CFC3AE`/`#E4DAC8`) first, soft low-opacity shadows only on light grounds. Tiny radii 2-6px. Mark never recolored/rotated/scaled, 1:1, 25% clear space. Flat colors from `palette.json` only.
- **Palette (authoritative hexes):** paper `#FBF6EC`, paper-2 `#F3EDE1`, card `#FFFDF7`, ink `#2A2521`, ink-soft `#4A4238`, clay `#8A7B6C`, ochre `#B5862E` (display-only), ochre-deep `#8A6520` (AA text), sage `#7C8A6B` (display-only), sage-deep `#5F6C50` (AA text), line `#E4DAC8`, line-strong `#CFC3AE`.
- **Typography (typography.md):** Latin display = Bricolage Grotesque; Arabic display = El Messiri; Latin body = Public Sans; Arabic body = Noto Sans Arabic. **Bilingual copy:** English is the display primary, Arabic accent words (e.g. مسارك) in El Messiri ochre-deep. Arabic RTL, no italics/slant, letter-spacing 0 in Arabic, no ALL CAPS in Arabic, English Sentence case. Real brand fonts ARE installed (`~/.local/share/fonts/ElMessiri.ttf`, `PublicSans.ttf`, `BricolageGrotesque.ttf`) + Noto Sans Arabic system-wide. Bricolage must never render Arabic; El Messiri must never render Latin.
- **Version/output:** 1920x1080, 30 fps, ~60s target (±5s), H.264 high profile `yuv420p`, AAC 192k, `-movflags +faststart`. Deliverable `brand/video/skillsynth-promo.mp4`.
- **Language: bilingual EN+AR mix.** Every title card shows English display + an Arabic accent line (or vice versa). No invented/fake capabilities: on-screen feature labels correspond to real captured screens.
- **Credential hygiene:** `belt` token stays in `~/.config/inference.sh/`; never write keys into the repo or tracked files.
- **Audio:** I source a CC0/royalty-free warm music bed from the web (verify license, record attribution). No voiceover.

---

## File / Artifact Structure
```
brand/video/
  skillsynth-promo.mp4            # FINAL deliverable
  README.md                       # how it was made, music attribution, re-render cmd
  work/                           # working outputs (gitignore-able)
    frames/                       # PIL title cards + section cards (1920x1080)
    ai/                           # AI clips intro.MP4 / outro.MP4
    screens/                      # chrome-devtools captures (*.png)
    clips/                        # per-beat ffmpeg segments + picture_only.mp4
    audio/                        # track + attribution.txt
  scripts/
    capture.py                    # (skip — chrome-devtools orchestrated by controller)
    make_cards.py                 # PIL bilingual title cards
    render.sh                     # ffmpeg Ken Burns -> clips -> xfade -> final mux
    verify.sh                     # ffprobe checks + contact sheet
```
Note: `brand/` has no `video/` dir yet; this plan creates `brand/video/` (+`work/`).

---

## Task 1: Seed & launch the app stack (capture ground truth)
**Interfaces:** Produces running backend :8000 + frontend :3000 (+admin :3001 as needed) with seeded demo data and known logins.

- [ ] **Step 1:** Verify belt + brand fonts ready (`belt app list --category video` no auth error; `fc-list` shows ElMessiri/PublicSans/Bricolage/NotoSansArabic).
- [ ] **Step 2:** From repo root seed + start backend (`PYTHONPATH=src python seed_v4.py`; `PYTHONPATH=src python run.py`) and frontend (`cd src/frontend && pnpm dev --port 3000`). Confirm ports listen.
- [ ] **Step 3:** Smoke-test `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000` -> 200.
- [ ] **Step 4:** Confirm logins `demo@demo.com`/`demo123` and `admin@skillsynth.io`/`Admin@123456` work.
- [ ] **Step 5:** Commit scaffold.

## Task 2: Generate AI abstract intro/outro textures (belt)
**Interfaces:** Consumes belt auth. Produces `work/ai/intro.MP4`, `outro.MP4` abstract clips used behind bookends.

- [ ] **Step 1:** Draft Warm-Craft abstract prompt (paper tones, ochre/sage, sprout rising, no text, no people).
- [ ] **Step 2:** `belt app run google/veo-3-1-fast --input '{"prompt":"<prompt>","duration":8}'` -> fetch asset to `work/ai/intro.MP4` (per `belt app run`/`belt files --help`).
- [ ] **Step 3:** Same for `outro.MP4` (closing/settling variant).
- [ ] **Step 4:** `ffprobe` verify both clips exist (any 480p-1080p acceptable; subtle background only). Fallback: `bytedance/seedance-2-0` or `falai/wan-2-5`; if all AI fails, mark bookends for programmatic fallback (Task 5 approach B).
- [ ] **Step 5:** Commit.

## Task 3: Capture real app screens (chrome-devtools + controller)
**Interfaces:** Consumes Task 1 app. Produces 1920x1080 stills of every showcase page/state with correct role + RTL.
Implementation by controller using chrome-devtools tools (`new_page`/`navigate_page`, `resize_page` 1920x1080, `fill_form`/`click` to log in + reach state, `take_screenshot` full/viewport) — this orchestration is done by the coordinator, not a subagent.

- [ ] **Step 1:** Login as demo; capture landing, login, register, dashboard.
- [ ] **Step 2:** Wizard flow: job -> QuizStep -> ReviewStep.
- [ ] **Step 3:** Learner pages: catalog, skill detail, learn, analytics, profile, settings.
- [ ] **Step 4:** Login as admin; capture users, skills, categories, job-roles, resources, paths, assessments, reports, feature-flags, health, audit-logs, db-inspector, backups, admin dashboard.
- [ ] **Step 5:** Verify all captured PNGs are 1920x1080 (via PIL), none blank.
- [ ] **Step 6:** Commit.

## Task 4: Build bilingual title cards (PIL, subagent)
**Files:** `brand/video/scripts/make_cards.py`; outputs `work/frames/{welcome,close,section-01..0N}.png`.
**Interfaces:** Consumes palette.json + fonts + (bookend AI clips as backdrops later). Produces branded 1920x1080 cards.

Bilingual copy (English display + Arabic accent, per identity):
- Welcome: **SkillSynth** (Bricolage, "Synth" ochre-deep) + Arabic tagline with accent word, e.g. "منصة تعلّم تُكيّف مسارك لك" (مسارك in El Messiri ochre-deep).
- Section dividers: "Discover · Learn · Grow" + "اكتشف · تعلّم · انمُ"; "Admin tools" + "الأدوات الإدارية".
- Closing: mark + **SkillSynth** + Arabic line "مسار من ما تعرفه إلى ما يمكنك أن تصبح" + English logline.

- [ ] **Step 1:** Write `make_cards.py`: pure-PIL card renderer (paper bg, mark from `mark-only.png`, real fonts, hairline rules, card/inset surfaces, palette tokens).
- [ ] **Step 2:** Run; verify all cards 1920x1080, Arabic+English render (no tofu), on-brand.
- [ ] **Step 3:** Commit.

## Task 5: Assemble the ~60s edit (ffmpeg, subagent)
**Files:** `brand/video/scripts/render.sh`; outputs `work/clips/seg-*.mp4`, `picture_only.mp4`; final `skillsynth-promo.mp4` (audio added in Task 7).
**Interfaces:** Consumes Task 2 clips, Task 3 screens, Task 4 cards (Task 4 outputs referenced by exact relative path `../work/...`; Task 3 screens path `work/screens/*.png`). Produces picture-only edit then (Task 7) final mux.

Timeline (~60s @30fps), beats:
1. **Welcome** ~6s (AI intro + welcome card, slow zoom/pan)
2. **Login -> Dashboard** ~8s
3. **Wizard** (job->quiz->review) ~9s
4. **Discover** (catalog -> skill detail) ~8s
5. **Learn** ~6s
6. **Analytics** ~6s
7. **Admin tools** (users/skills, reports, health) ~9s
8. **Closing** ~8s (outro AI + close card)

- [ ] **Step 1:** Write `render.sh` using `zoompan` per beat (1920x1080@30), chain with `xfade`, output `work/clips/picture_only.mp4` ~60s.
- [ ] **Step 2:** `ffprobe` duration ~58-62s.
- [ ] **Step 3:** Extract a few frames, verify legibility + on-brand.
- [ ] **Step 4:** Commit.

## Task 6: Source & mix CC0/royalty-free music (controller/web)
**Files:** `work/audio/track.*` + `attribution.txt`.
**Interfaces:** Produces audio bed for Task 7 mux. Sourced by controller via `websearch`/`webfetch` (Pixabay Music, FMA, Incompetech — verify license & attribution).

- [ ] **Step 1:** Locate CC0/royalty-free warm, understated ~60s bed (not AI-generated).
- [ ] **Step 2:** Download to `work/audio/`, write `attribution.txt`.
- [ ] **Step 3:** `ffprobe` verify audio stream loads.
- [ ] **Step 4:** Commit.

## Task 7: Final encode & mux (ffmpeg, subagent)
**Files:** `brand/video/skillsynth-promo.mp4` (final).
**Interfaces:** Consumes Task 5 `picture_only.mp4` + Task 6 audio.

- [ ] **Step 1:** Mux: `ffmpeg -i picture_only.mp4 -i track.* -filter_complex "[1:a]aresample=48000,volume=0.6[a]" -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart brand/video/skillsynth-promo.mp4`.
- [ ] **Step 2:** Verify final spec (duration ~60s, 1920x1080@30 h264 yuv420p, aac 48k/192k).
- [ ] **Step 3:** Contact sheet + final visual QA.
- [ ] **Step 4:** Commit.

## Task 8: Wrap-up, attribution, optional variants
- [ ] **Step 1:** Write `brand/video/README.md` (sources: AI models, music attribution, render cmd `bash brand/video/scripts/render.sh`, brand guardrails).
- [ ] **Step 2:** Optional 9:16 + 4K variants only if requested (not default).
- [ ] **Step 3:** Commit.
