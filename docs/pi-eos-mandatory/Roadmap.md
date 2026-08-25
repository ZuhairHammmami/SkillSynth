# Roadmap

## Phase 1: Foundation ✅ (Complete)
- FastAPI Clean Architecture (20 layers, 85 routes)
- 32-table 3NF database with seed script
- JWT auth with RBAC (6 roles, 51 permissions)
- SSE + WebSocket real-time infrastructure

## Phase 2: Learning Engine ✅ (Complete)
- Deterministic path generation (topological sort)
- Skill prerequisite DAG with 102 skills
- Assessment engine with adaptive scoring
- Resource recommender with preference filtering

## Phase 3: Frontend ✅ (Complete)
- Next.js 14 App Router with 24 routes
- 3 route groups: auth, student, admin
- Feature-sliced design with shared component library
- 100% Arabic/English i18n with dynamic RTL

## Phase 4: Admin Portal ✅ (Complete)
- 11 admin pages with separate layout/nav
- User, skill, category, path, resource CRUD
- Audit log with SSE streaming
- Analytics dashboard with real-time metrics

## Phase 5: Polish (Current)
| Task | Status |
|------|--------|
| Pydantic V2 migration | ✅ Complete |
| Alembic initialization | ✅ Complete |
| PI-EOS v2.0 mandatory docs | ✅ Complete |
| Deprecated gamification cleanup | ✅ Verified |
| Empty layer implementation/removal | ⬜ Pending |
| Production deployment hardening | ⬜ Planned |
| Performance optimization | ⬜ Planned |

## Phase 6: Production (Next)
- [ ] Full end-to-end testing (Playwright)
- [ ] Performance load testing (k6)
- [ ] Security penetration testing
- [ ] Production deployment to Render + Vercel
- [ ] Monitoring and alerting setup
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Documentation finalized

## Phase 7: Enhancement (Future)
- [ ] Multi-factor authentication
- [ ] Team/org management (multi-tenant)
- [ ] Custom skill taxonomy (admin-defined)
- [ ] Learning path sharing between users
- [ ] API rate limiting with Redis backend
- [ ] Full-text search on resources
- [ ] PDF/offline export of learning paths
