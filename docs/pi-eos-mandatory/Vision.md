# Vision

## SkillSynth — Adaptive Learning OS

**Mission**: Build an enterprise-grade adaptive learning platform that synthesizes personalized career paths through deterministic AI-driven skill gap analysis, prerequisite-aware topological sorting, and real-time progress tracking — without gamification noise.

## Core Philosophy

> **Learning is not a game. It's a craft.**

SkillSynth removes XP, streaks, badges, and leaderboards. Instead, it provides:
- **Deterministic path generation** — Same inputs always produce same outputs
- **Prerequisite-aware DAG resolution** — Topological sort ensures no circular dependencies
- **Real skill assessment** — Adaptive questioning calibrated to actual proficiency
- **Enterprise analytics** — Real metrics, not vanity numbers

## Target Users

| Persona | Needs | SkillSynth Delivers |
|---------|-------|---------------------|
| **Career Switcher** | Structured path from current skills to target role | Gap analysis → topological path → curated resources |
| **Junior Developer** | Know what to learn next, in what order | Prerequisite graph + weekly time budgeting |
| **Engineering Manager** | Team skill visibility, hiring benchmarks | Admin analytics, role definitions, skill taxonomy |
| **Self-Directed Learner** | Arabic/English, RTL/LTR, offline-capable | 100% i18n, PWA-ready, SSE real-time sync |

## Success Metrics (Non-Gamified)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Path completion rate | >40% | Step completions / total steps |
| Assessment accuracy | >85% correlation | Post-path skill verification |
| Time to first path | <5 min | Wizard completion latency |
| API P95 latency | <200ms | /api/learning/graph, /api/analytics/dashboard |
| Uptime | 99.9% | Health endpoint monitoring |

## Anti-Goals

- ❌ No XP, points, levels, streaks as primary motivators
- ❌ No leaderboards or social competition
- ❌ No random rewards or loot boxes
- ❌ No "engagement" dark patterns
- ❌ No free-text career input (structured selection only)

## Strategic Differentiators

1. **Deterministic Engine** — No LLM hallucination in path generation
2. **Strict 3NF Database** — 32 tables, zero JSON bridges, zero denormalization
3. **Clean Architecture** — 20 layers, <300 lines/file, <40 lines/function
4. **Admin/Student Separation** — Two distinct applications, zero feature bleed
5. **Arabic-First RTL** — Not an afterthought; Tajawal font, dynamic dir switching