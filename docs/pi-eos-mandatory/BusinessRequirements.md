# Business Requirements

## Product Overview

SkillSynth is a B2B SaaS adaptive learning platform for technical skill acquisition. Primary revenue model: per-seat subscription for engineering teams.

## Revenue Model

| Tier | Price (Monthly) | Features |
|------|-----------------|----------|
| **Free** | $0 | 1 active path, basic analytics, community resources |
| **Pro** | $29/user | Unlimited paths, advanced analytics, priority resources, API access |
| **Enterprise** | Custom | SSO, custom roles, dedicated support, SLA, on-premise option |

## Market Positioning

- **Not**: Coursera/Udemy (content marketplace)
- **Not**: LeetCode/CodeSignal (assessment only)
- **Is**: "GPS for technical careers" — tells you exactly what to learn, in what order, with what resources

## Key Business Rules

1. **Career Selection Flow** (mandatory, no shortcuts):
   ```
   Career Selection → Preferences → Assessment → Path Generation
   ```
2. **Admin ≠ Student** — Separate applications, separate data views
3. **No Gamification** — No XP, streaks, achievements in core loop
4. **Bilingual Mandatory** — AR/EN parity for all user-facing text
5. **Data Ownership** — User data exportable, GDPR-compliant

## Stakeholders

| Role | Interest |
|------|----------|
| Engineering Managers | Team skill visibility, hiring plans |
| HR/L&D | Upskilling ROI, compliance tracking |
| Individual Contributors | Career clarity, structured learning |
| Platform Admins | System health, user management, content curation |

## Constraints

- **Tech Stack**: FastAPI + Next.js 14 (non-negotiable)
- **Database**: PostgreSQL production, SQLite dev
- **Deployment**: Render (backend) + Vercel (frontend)
- **Latency Budget**: API P95 < 200ms, LCP < 1.5s