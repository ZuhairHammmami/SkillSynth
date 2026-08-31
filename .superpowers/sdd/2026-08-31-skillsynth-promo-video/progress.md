# SDD ledger — plan: docs/superpowers/plans/2026-08-31-skillsynth-promo-video.md

## Preflight scan
No interdependent software files; tasks share media artifacts only. No plan-vs-constraint conflicts after rulings below.

## Rulings
- Bilingual EN+AR copy (user): English display primary + Arabic accents, per identity - overrides plan's earlier Arabic-only note.
- Audio provided by controller (user choice A): CC0/royalty-free sourced by me.
- Execution: sub-agents for cards (T4), assembly (T5), final mux (T7), README (T8); controller handles app launch, belt AI, chrome-devtools capture, music - steps too interactive/non-deterministic for mechanical subagents.
- Task 3 capture method: chrome-devtools MCP unusable (no Chrome at /opt/google/chrome/chrome; /opt not writable without sudo; config change needs opencode restart). Ruling: Playwright (Python) driving system /usr/bin/chromium headless at force-device-scale-factor=1. Cost if wrong: replay capture with different browser tooling.

## Task 1: complete (controller) - app stack up, backend :8000 + frontend :3000 + admin :3001, seeded 1999 rows, endpoints 200.

## Task 2: Ruling - belt AI blocked: inference.sh balance $0.00, min $0.50 required for belt app run. Plan pre-defined fallback (approach B): programmatic ffmpeg abstract texture clips for bookends. Cost if wrong: bookends lose AI-generated realism; brand-consistent motion retained.
## Task 2: complete (controller fallback) - programmatic abstract intro/outro textures to be generated as components.

## Task 2: complete - programmatic ffmpeg gradient+noise abstract clips (intro 8s paper/ochre, outro 6s paper/sage), both 1920x1080@30, verified on-brand palette.

## Task 3: complete (controller via playwright) - 33 screens, all 1920x1080 non-blank, committed ba90b071. Screens: landing, login, register, dashboard, wizard-{job,field,role,self,preferences,review}, catalog, catalog-category, catalog-skill, learn, analytics, profile, settings, admin-{login,dashboard,users,skills,categories,job-roles,resources,paths,assessments,reports,feature-flags,health,audit-logs,db-inspector,backups,settings}.

## Task 4: complete (subagent eb7aaf41, controller-verified) - make_cards.py + 4 frames (welcome, section-discover, section-admin, close). Re-ran script: all 1920x1080, cmap OK (no tofu), RTL mixed-line delta 0, non-blank. Section cards got a small 160px mark (implementer concern, on-brand, accepted).
