# SS-EDS: Error Handling

## Purpose
Document the error handling strategy across all layers: FastAPI exception handlers with safe-serialized responses, service-level fallback pattern (no throws), frontend ErrorBoundary components, and React Query error handling.

## Responsibilities
- Handle and log all API errors with appropriate HTTP status codes
- Provide safe-serialized error responses (no Pydantic/SQLAlchemy internals)
- Implement graceful degradation for service failures
- Maintain ErrorBoundary components for UI resilience (3 variants)
- Ensure services never throw — return fallback/empty results
- Log all errors with traceback for debugging

## Inputs
- Exception types (HTTPException, RequestValidationError, ValidationError)
- Service failure scenarios (DB down, missing data, timeout)
- Network error patterns (offline, timeout, 5xx)
- Form validation error details

## Outputs
- Error response schemas with detail and field-level errors
- ErrorBoundary fallback UI components
- Error logs and audit trail entries
- User-friendly error notifications

## Dependencies
- 07-backend (exception handlers in main.py, service fallbacks)
- 08-frontend (ErrorBoundary, error pages, React Query error states)
- 18-monitoring (error tracking and logging)

## Sequence: Error Handling Flow
```
Request → FastAPI Route → Service → Exception → Exception Handler
                                                     ↓
                                              Log Error + Traceback
                                                     ↓
                                            Safe-serialize response
                                                     ↓
                                          Return JSON error to client
                                                     ↓
                                          Frontend → ErrorBoundary or Toast
                                                     ↓
                                          User-friendly notification
```

## HTTP Status Code Mapping
| Status | Condition | Response |
|--------|-----------|----------|
| 400 | Bad request / validation | detail message + field errors array |
| 401 | Missing/invalid token | "Not authenticated" |
| 403 | Insufficient permissions | "Permission denied" |
| 404 | Resource not found | "Not found" |
| 409 | Conflict (duplicate, FK violation) | detail message |
| 422 | Request validation error | Safe-serialized field errors |
| 429 | Rate limit exceeded | Retry-After header + message |
| 500 | Internal server error | Generic message (full error logged) |

## Frontend Error States
| Component | Error State | Behavior |
|-----------|-------------|----------|
| AuthGuard | isAuthenticated false | Skeleton → Redirect to /login |
| ErrorBoundary (generic) | Unhandled React error | "System Noise — Unexpected Interference" |
| ErrorBoundary (analytics) | Chart render failure | "Signal Lost" |
| ErrorBoundary (DAG) | Graph visualization crash | "Circuit Error" |
| React Query queries | API fetch failure | Retry 2× → Show toast error |
| React Query mutations | API write failure | Show toast with server detail message |

## Service Fallback Pattern
All Python services follow: never throw exceptions — return fallback/empty result + log warning.
```python
def some_service(db, param):
    try:
        result = do_work(db, param)
        return result
    except Exception:
        logger.warning(f"Service failed for {param}", exc_info=True)
        return []
```

## Rules
1. Never expose internal error details to client (Pydantic, SQLAlchemy internals)
2. All server errors must be logged with full traceback
3. Frontend must always show user-friendly message on any error
4. Form validation errors must be field-specific with field names
5. Services must have fallback (never throw — return empty/None)
6. 500 errors must mask internal details with generic message

## Examples
- Validation error: make_json_safe() strips Pydantic internals before serialization
- Rate limiting: 429 with Retry-After header, frontend shows countdown toast
- Service fallback: LearningEngine.get_prerequisite_chain returns [] on DB failure

## Edge Cases
- Concurrent validation errors → array of per-field error details
- Network timeout during upload → retry with progress indicator
- Database deadlock → SQLAlchemy automatic retry (configurable)
- Error in error handler → logged as double-fault, generic 500 returned

## Failure Cases
- ErrorBoundary catches but cannot recover → shows fallback UI, no crash
- Log service fails → errors still returned to client but not persisted
- Validation error exposes Pydantic internals → must use safe serializer
- Service throws instead of returning fallback → 500 error to client

## Recovery Procedures
1. Check server logs for exception traceback and correlation
2. Reproduce error in development environment
3. Fix root cause and verify with manual test
4. Add regression coverage if missing

## Refactoring Strategy
- Add structured error codes for machine-readable error handling
- Implement retry middleware for transient failures
- Add error correlation IDs for request tracing across services
- Centralize error response format in shared schema
