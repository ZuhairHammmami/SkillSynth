# SS-EDS: Monitoring

## Purpose
Document the monitoring, observability, and alerting strategy for SkillSynth. Covers API response time tracking, error logging, audit log review, and system health reporting.

## Responsibilities
- Monitor API endpoint response times
- Track error rates and types
- Maintain audit log for security and compliance
- Generate system health reports
- Alert on performance degradation or service outages

## Inputs
- API request/response data
- Error logs from exception handlers
- Audit log entries (events table)
- User-reported issues

## Outputs
- System health metrics
- Audit log reports
- Performance dashboards
- Alert notifications

## Dependencies
- 07-backend (error logging, exception handlers)
- 10-database (events table for audit)
- 27-analytics (dashboard metrics)
- 17-deployment (infrastructure monitoring)

## Sequence: Incident Detection Flow
```
API Request → FastAPI → Error → Exception Handler → Log Error → events table (category="error") → Alert → Investigation
```

## State Diagram: Service Health
```
[Healthy] → [Degraded] → [Down] → [Recovering] → [Healthy]
     ↓            ↓           ↓
[Warning]    [Critical]   [Incident]
```

## Monitoring Targets
| Metric | Target | Method |
|--------|--------|--------|
| API p95 response time | < 200ms | Request timing middleware |
| Error rate | < 0.1% | Exception handler logging |
| Uptime | 99.9% | Health check endpoint |
| Lighthouse | 100/100/100/100 | Automated audit |
| Audit log completeness | 100% of admin actions | events table category="audit" |

## ERD References
- events table: category="audit" for admin actions, "error" for system errors
- Admin reports: GET /api/admin/reports/system-health

## Rules
1. All errors must be logged with stack trace
2. Admin actions must create audit log entries
3. System health report must be available at all times
4. Rate limit violations must be logged
5. Authentication failures must be logged (without password exposure)

## Examples
- Exception handler in main.py: logs generic 500 errors with traceback
- Audit log: `{category:"audit", action:"user_created", entity_type:"profile", entity_id:42, ip_address:"192.168.1.1"}`

## Edge Cases
- High-frequency errors causing log flooding → rate-limited error logging
- Database connection failure → cannot write audit log → buffer in memory
- Audit log table growing unbounded → need retention policy

## Failure Cases
- Monitoring itself fails (silent outage)
- Log storage exhausted
- Alert system sends too many false positives

## Recovery Procedures
1. Check /api/admin/reports/system-health endpoint
2. Review database connection pool status
3. Check server resource utilization (CPU, memory, disk)
4. Implement log rotation and retention

## Refactoring Strategy
- Add structured logging (JSON format) for log aggregation
- Integrate with external monitoring (Datadog, Sentry, Grafana)
- Implement automated alerting via webhook (Slack/Email)
- Add distributed tracing for request lifecycle
