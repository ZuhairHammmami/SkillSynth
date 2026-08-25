# System Context

SkillSynth operates in the following context:

## External Systems
| System | Integration | Protocol |
|--------|-------------|----------|
| **SQLite** (dev) | Local file `skillsynth.db` | SQLAlchemy ORM |
| **PostgreSQL** (prod) | Supabase/Render hosted | SQLAlchemy ORM (pool_size=10) |
| **Browser** | Next.js SSR + client hydratio | HTTP+REST + SSE + WebSocket |
| **LLM Providers** (optional) | OpenAI/Ollama (path enrichment) | REST API (langchain) |
| **SendGrid** (email) | Password reset emails | REST API (sendgrid) |

## Internal Boundaries
| Boundary | Owns | Consumers |
|----------|------|-----------|
| **Auth Context** | JWT, sessions, roles, permissions | All routers |
| **Learning Context** | Skills, paths, assessments, resources | Student app |
| **Admin Context** | Users, roles, system config, analytics | Admin app |
| **Event Context** | SSE streams, notifications, audit | Both apps |

## Environment Matrix
| Env | Backend | Frontend | DB |
|-----|---------|----------|----|
| Development | localhost:8000 | localhost:3000 | skillsynth.db |
| Staging | render.com | vercel.com | Supabase (staging) |
| Production | render.com | vercel.com | Supabase (production) |

## Deployment Topology
```
git push → GitHub
  → Render: FastAPI (gunicorn + uvicorn workers)
  → Vercel: Next.js (SSR/ISR)
  → Supabase: PostgreSQL (pooled connections)
```
