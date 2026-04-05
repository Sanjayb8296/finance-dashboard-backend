# Core Module

Shared infrastructure used by all other modules. No business logic lives here.

## Directory Structure

```
core/
├── __init__.py
├── models.py              # TimestampedModel, SoftDeleteModel, SoftDeleteManager
├── exceptions.py          # ApplicationError, PermissionDeniedError, NotFoundError, etc.
├── exception_handler.py   # Wraps all errors into consistent envelope
├── renderers.py           # ApiRenderer — wraps success responses
├── pagination.py          # StandardPagination (20/page, max 100)
├── throttling.py          # RoleBasedThrottle (per-role rate limits)
├── middleware.py           # SentryUserContextMiddleware (optional)
└── views.py               # HealthCheckView
```

## Responsibilities

- Abstract base models (timestamps, soft delete)
- Custom exception classes and DRF exception handler
- Consistent response envelope via custom renderer
- Pagination defaults
- Role-based throttling
- Health check endpoint
- Sentry middleware (conditional, graceful when disabled)

## Files

| File | Purpose |
|------|---------|
| `models.py` | `TimestampedModel` (created_at, updated_at) and `SoftDeleteModel` (is_deleted, deleted_at) with `SoftDeleteManager` that filters out deleted rows by default |
| `exceptions.py` | `ApplicationError`, `PermissionDeniedError`, `NotFoundError`, `ValidationError`, `ConflictError` — all extend DRF's `APIException` |
| `exception_handler.py` | Wraps all error responses into `{"success": false, "message", "data": null, "errors"}`. Logs unhandled exceptions |
| `renderers.py` | `ApiRenderer` wraps successful responses into `{"success": true, "message", "data", "errors": null}` |
| `pagination.py` | `StandardPagination` — page size 20, max 100, configurable via `page_size` query param |
| `throttling.py` | `RoleBasedThrottle` — rate limits per role (viewer: 100/hr, admin: 500/hr, anon: 30/hr). Rates configured in `config/settings/base.py` |
| `middleware.py` | `SentryUserContextMiddleware` — attaches user ID/email/role to Sentry events. Gracefully skips if sentry_sdk is not installed |
| `views.py` | `HealthCheckView` — unauthenticated GET `/api/v1/health/` returning DB connection status |

## Response Envelope

Every API response follows this format:

```json
{"success": true/false, "message": "...", "data": {}, "errors": null}
```

Successful responses are wrapped by `ApiRenderer`. Errors are wrapped by `custom_exception_handler`.

## Soft Delete

Models inheriting `SoftDeleteModel` get:
- `objects` manager — returns only non-deleted rows (default)
- `all_objects` manager — returns all rows including deleted
- `soft_delete()` / `restore()` instance methods

## Throttle Rates

Configured in `config/settings/base.py`, enforced by `RoleBasedThrottle`:

| Role | Rate |
|------|------|
| Viewer | 100/hour |
| Analyst | 200/hour |
| Manager | 300/hour |
| Admin | 500/hour |
| Auditor | 200/hour |
| Anonymous | 30/hour |

Throttling is disabled in development (`config/settings/development.py`).

## Links to Other Modules

- **config/** — References `ApiRenderer`, `custom_exception_handler`, `StandardPagination`, `RoleBasedThrottle` in REST_FRAMEWORK settings
- **users/** — `User` model inherits from `TimestampedModel`
- **records/** — `FinancialRecord` inherits from `TimestampedModel` + `SoftDeleteModel`; services raise `NotFoundError`, `PermissionDeniedError`
- **audit/** — `AuditLog` inherits from base model; services raise core exceptions
- **dashboard/** — Selectors use `FinancialRecord` which inherits from core base models
