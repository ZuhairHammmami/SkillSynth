# Monitoring Guide

## Health Endpoints
| Endpoint | Purpose |
|----------|---------|
| `GET /` | Root health check: returns `{"status": "operational"}` |
| `GET /api/admin/reports/system-health` | Database status, user/path/assessment counts |

## Logging
- **Framework**: Python `logging` module with structured JSON format
- **Level**: INFO for normal operations, ERROR for exceptions
- **Location**: Console/stdout (captured by Render/Vercel)
- **Audit**: All mutations logged to `audit_logs` table

## Metrics to Track
| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| API Error Rate | FastAPI exception handlers | >1% of requests |
| API P95 Latency | Application logs | >500ms |
| DB Connection Pool | `pool_size=10`, `max_overflow=20` | Pool exhaustion |
| User Registrations | `audit_logs` table | Spike detection |
| Active Users (7d) | `step_completions` table | Drop >50% |

## Alerting
- **Error rate** >1% → Slack/webhook notification
- **Rate limit hits** >10% of auth requests → Investigation needed
- **SSE disconnects** >5% of connections → Check realtime_router

## Runbooks
See `docs/42-runbooks/` for operational procedures.
