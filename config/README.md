# Config Module

Django project configuration with environment-based settings split, URL routing, and WSGI/ASGI entry points.

## Directory Structure

```
config/
├── __init__.py
├── settings/
│   ├── __init__.py
│   ├── base.py            # Shared settings (all environments)
│   ├── development.py     # Local dev overrides
│   └── production.py      # Production overrides
├── urls.py                # Root URL configuration
├── wsgi.py                # WSGI entry point
└── asgi.py                # ASGI entry point
```

## Settings Architecture

Settings follow a **base → override** pattern. `base.py` defines all shared configuration, while `development.py` and `production.py` import everything from base and override only what differs.

### `base.py` — Shared Configuration

| Section | Details |
|---------|---------|
| **Installed Apps** | DRF, SimpleJWT (with token blacklist), django-filter, drf-spectacular, and all local apps (core, users, records, dashboard, audit) |
| **REST Framework** | JWT auth, `IsAuthenticated` default, `StandardPagination` (20/page), `ApiRenderer`, `custom_exception_handler`, role-based throttling |
| **JWT** | 30-min access token, 7-day refresh, rotation + blacklisting enabled, `Bearer` scheme |
| **drf-spectacular** | OpenAPI 3.0 spec titled "Finance Dashboard API", 6 tag groups, JWT security scheme, request/response component split |
| **Throttling** | Per-role rates: viewer 100/hr, analyst 200/hr, manager 300/hr, admin 500/hr, auditor 200/hr, anon 30/hr |
| **Logging** | Console handler, verbose format (`{levelname} {asctime} {module} {message}`), INFO level |
| **Sentry** | Commented out — uncomment and set `SENTRY_DSN` env var to enable error monitoring |

### `development.py` — Local Development

- `DEBUG = True`
- PostgreSQL on `localhost:5432`
- Throttling disabled for easier testing

### `production.py` — Production

- `DEBUG = False`
- PostgreSQL via environment variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- Security hardening: XSS filter, content type sniffing protection, secure cookies, `X-Frame-Options: DENY`

## URL Routing

Defined in `urls.py`. All API endpoints are namespaced under `/api/v1/`.

| Pattern | Target | Description |
|---------|--------|-------------|
| `api/v1/` | `users.api.urls` | Auth + user management |
| `api/v1/` | `records.api.urls` | Financial records |
| `api/v1/` | `dashboard.api.urls` | Analytics dashboard |
| `api/v1/` | `audit.api.urls` | Audit trail |
| `api/v1/health/` | `HealthCheckView` | System health check |
| `api/schema/` | `SpectacularAPIView` | OpenAPI 3.0 JSON schema |
| `api/docs/` | `SpectacularSwaggerView` | Swagger UI |
| `api/redoc/` | `SpectacularRedocView` | ReDoc documentation |
| `admin/` | Django Admin | Admin panel |

## Environment Variables

| Variable | Default | Used In |
|----------|---------|---------|
| `SECRET_KEY` | `django-insecure-dev-key...` | base.py |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | base.py |
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` | wsgi.py, asgi.py |
| `DB_NAME` | `finance_db` | production.py |
| `DB_USER` | `postgres` | production.py |
| `DB_PASSWORD` | `postgres` | production.py |
| `DB_HOST` | `db` | production.py |
| `DB_PORT` | `5432` | production.py |
| `SENTRY_DSN` | (empty) | base.py |
| `DJANGO_ENV` | `development` | base.py (Sentry) |

## Switching Environments

```bash
# Local development (default)
export DJANGO_SETTINGS_MODULE=config.settings.development

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
```

## Links to Other Modules

- **core/** — Provides `ApiRenderer`, `custom_exception_handler`, `StandardPagination`, `RoleBasedThrottle` referenced in REST_FRAMEWORK settings
- **users/** — Auth and user routes included via `users.api.urls`
- **records/** — Financial record routes included via `records.api.urls`
- **dashboard/** — Analytics routes included via `dashboard.api.urls`
- **audit/** — Audit trail routes included via `audit.api.urls`
