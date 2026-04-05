# Finance Data Processing & Access Control System

A Django REST Framework backend for a finance dashboard with role-based access control, financial record management, analytics, and audit trail.

## Features

- **5-Role Access Control**: VIEWER, ANALYST, MANAGER, ADMIN, AUDITOR with defense-in-depth (4 layers)
- **Financial Records CRUD**: Create, read, update, soft-delete with filtering, search, and pagination
- **Dashboard Analytics**: Summary, monthly trends, category breakdown — all via DB-level aggregations
- **Audit Trail**: Full audit logging with field-level change tracking
- **JWT Authentication**: Register, login, refresh, logout with token blacklisting
- **API Documentation**: Swagger UI and ReDoc via drf-spectacular
- **CSV Export**: Export filtered records as CSV
- **Role-Based Throttling**: Per-role rate limits (100–500 req/hr)

## Documentation

| Document | Description |
|----------|-------------|
| [Swagger Setup](docs/swagger-setup.md) | OpenAPI 3.0 config, Swagger UI usage, schema decorators |
| [JWT Authentication](docs/jwt-authentication.md) | Token lifecycle, login/refresh/logout flow, security notes |
| [Sentry Setup](docs/sentry-setup.md) | Optional error monitoring with automatic enablement when `SENTRY_DSN` is set |
| [Throttling](docs/throttling.md) | Role-based rate limiting, configuration, development override |
| [Testing Guide](TESTING_GUIDE.md) | Test setup, execution steps, and validation workflow |
| [Config Module](config/README.md) | Project settings split, environment handling, and app configuration |
| [Core Module](core/README.md) | Shared infrastructure, exceptions, pagination, renderers, and middleware |
| [Users Module](users/README.md) | Authentication, user management, roles, permissions, and related APIs |
| [Records Module](records/README.md) | Financial record lifecycle, permissions, services, selectors, and APIs |
| [Dashboard Module](dashboard/README.md) | Analytics endpoints, aggregations, and dashboard data flow |
| [Audit Module](audit/README.md) | Audit logging design, actions, selectors, and audit APIs |

## Tech Stack

- Python 3.11+ / Django 5.x / Django REST Framework
- djangorestframework-simplejwt (JWT auth)
- django-filter (query filtering)
- drf-spectacular (OpenAPI 3.0 docs)
- pytest + factory-boy (testing)
- PostgreSQL

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed sample data (creates users for each role + financial records)
python manage.py seed_data

# Start server
python manage.py runserver
```

### Seed Data Credentials

After running `python manage.py seed_data`:

| Role    | Email               | Password   |
|---------|---------------------|------------|
| ADMIN   | admin@example.com   | admin123!  |
| MANAGER | manager@example.com | manager123!|
| ANALYST | analyst@example.com | analyst123!|
| VIEWER  | viewer@example.com  | viewer123! |
| AUDITOR | auditor@example.com | auditor123!|

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## API Endpoints

### Authentication
| Method | Endpoint                | Description          | Auth |
|--------|-------------------------|----------------------|------|
| POST   | /api/v1/auth/register/  | Register new user    | No   |
| POST   | /api/v1/auth/login/     | Login (JWT pair)     | No   |
| POST   | /api/v1/auth/refresh/   | Refresh access token | No   |
| POST   | /api/v1/auth/logout/    | Blacklist refresh    | Yes  |

### Users
| Method | Endpoint             | Description      | Roles          |
|--------|----------------------|------------------|----------------|
| GET    | /api/v1/users/me/    | Own profile      | All            |
| PATCH  | /api/v1/users/me/    | Update profile   | All            |
| GET    | /api/v1/users/       | List users       | ADMIN, AUDITOR |
| POST   | /api/v1/users/       | Create user      | ADMIN          |
| GET    | /api/v1/users/{id}/  | User detail      | ADMIN, AUDITOR |
| PATCH  | /api/v1/users/{id}/  | Update user      | ADMIN          |
| DELETE | /api/v1/users/{id}/  | Deactivate user  | ADMIN          |

### Financial Records
| Method | Endpoint                  | Description      | Roles                        |
|--------|---------------------------|------------------|------------------------------|
| GET    | /api/v1/records/          | List records     | ANALYST, MANAGER, ADMIN, AUDITOR |
| POST   | /api/v1/records/          | Create record    | MANAGER, ADMIN               |
| GET    | /api/v1/records/{id}/     | Record detail    | ANALYST, MANAGER*, ADMIN, AUDITOR |
| PATCH  | /api/v1/records/{id}/     | Update record    | MANAGER*, ADMIN              |
| DELETE | /api/v1/records/{id}/     | Soft delete      | MANAGER*, ADMIN              |
| POST   | /api/v1/records/bulk/     | Bulk create      | ADMIN                        |
| GET    | /api/v1/records/export/   | CSV export       | ANALYST, MANAGER, ADMIN, AUDITOR |

*MANAGER can only access own records

### Dashboard
| Method | Endpoint                          | Description          | Roles |
|--------|-----------------------------------|----------------------|-------|
| GET    | /api/v1/dashboard/summary/        | Financial summary    | All   |
| GET    | /api/v1/dashboard/trends/         | Monthly trends       | All   |
| GET    | /api/v1/dashboard/category-breakdown/ | Category breakdown | All  |
| GET    | /api/v1/dashboard/recent/         | Recent transactions  | All   |

### Audit
| Method | Endpoint                | Description      | Roles          |
|--------|-------------------------|------------------|----------------|
| GET    | /api/v1/audit/logs/     | List audit logs  | ADMIN, AUDITOR |
| GET    | /api/v1/audit/logs/{id}/| Audit log detail | ADMIN, AUDITOR |

### System
| Method | Endpoint          | Description  | Auth |
|--------|-------------------|--------------|------|
| GET    | /api/v1/health/   | Health check | No   |

## Architecture

```
Views → Services → Selectors → Models
```

- **Views**: Request/response only (thin controllers)
- **Services**: Business logic, permission guards, mutations
- **Selectors**: Read queries, filtering, DB aggregations
- **Models**: Schema definition only

### Access Control (4 Layers)

1. **View permission class** — Fast rejection
2. **Service-level guard** — Business rule enforcement
3. **Selector-level scoping** — Query filtering by role
4. **Object-level check** — Ownership verification

## Project Structure

```
├── config/                  # Project configuration
│   ├── settings/
│   │   ├── base.py          # Shared settings (JWT, DRF, throttling, logging)
│   │   ├── development.py   # Local dev (DEBUG, local DB, no throttling)
│   │   └── production.py    # Production (env vars, security hardening)
│   ├── urls.py              # Root URL routing + Swagger/ReDoc
│   ├── wsgi.py              # WSGI entry point
│   └── asgi.py              # ASGI entry point
│
├── core/                    # Shared infrastructure
│   ├── models.py            # TimestampedModel, SoftDeleteModel
│   ├── exceptions.py        # Custom exception classes
│   ├── exception_handler.py # Consistent error response wrapper
│   ├── renderers.py         # ApiRenderer (success response envelope)
│   ├── pagination.py        # StandardPagination (20/page, max 100)
│   ├── throttling.py        # RoleBasedThrottle
│   ├── middleware.py         # Sentry user context (optional)
│   └── views.py             # HealthCheckView
│
├── users/                   # Authentication & user management
│   ├── models/              # User model with Role enum
│   ├── services/            # Registration, auth, CRUD, profile
│   ├── selectors/           # User queries with filtering
│   ├── permissions/         # IsAdmin, IsAdminOrAuditor
│   ├── api/                 # Serializers, views, URL routing
│   ├── management/commands/ # seed_data command
│   └── tests/               # 27 tests (API + services)
│
├── records/                 # Financial record management
│   ├── models/              # FinancialRecord with soft delete + indexes
│   ├── services/            # CRUD + bulk create + audit logging
│   ├── selectors/           # Role-scoped queries + filtering
│   ├── permissions/         # CanView, CanCreate, CanModify, CanExport
│   ├── api/                 # Serializers, views, URL routing
│   └── tests/               # 38 tests (API + services + edge cases)
│
├── dashboard/               # Analytics (read-only, no models)
│   ├── selectors/           # DB aggregations (Sum, Avg, TruncMonth)
│   ├── api/                 # Serializers, views, URL routing
│   └── tests/               # 8 tests
│
├── audit/                   # Audit trail
│   ├── models/              # AuditLog with AuditAction enum
│   ├── services/            # audit_service.log() called by other modules
│   ├── selectors/           # Filtered audit log queries
│   ├── api/                 # Serializers, views, URL routing
│   └── tests/               # 8 tests
│
├── conftest.py              # Pytest fixtures (user factories, API clients)
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── manage.py                # Django management entry point
```

## Infrastructure

### Database

PostgreSQL is used in all environments.

- **Development**: Direct connection to local PostgreSQL (`localhost:5432`)
- **Production**: Configured via environment variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)

### Settings Split

| File | `DEBUG` | Database | Throttling | Security |
|------|---------|----------|------------|----------|
| `base.py` | — | — | Role-based rates | — |
| `development.py` | `True` | Local PostgreSQL | Disabled | Default |
| `production.py` | `False` | Env var PostgreSQL | Inherited from base | XSS, CSRF, secure cookies, X-Frame-Options |

### JWT Configuration

| Setting | Value |
|---------|-------|
| Access token lifetime | 30 minutes |
| Refresh token lifetime | 7 days |
| Token rotation | Enabled |
| Blacklisting on rotation | Enabled |
| Auth header | `Authorization: Bearer <token>` |

### Throttle Rates

| Role | Rate |
|------|------|
| Viewer | 100/hour |
| Analyst | 200/hour |
| Manager | 300/hour |
| Admin | 500/hour |
| Auditor | 200/hour |
| Anonymous | 30/hour |

## Running Tests

```bash
pytest
pytest -v                    # Verbose
pytest users/tests/          # Specific app
pytest -k "permission"       # Filter by name
```

**Test coverage**: 90 tests across all modules — permissions, services, API endpoints, edge cases, and aggregations.

## Environment Variables

See `.env.example` for all available configuration options.

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | dev key | Django secret key |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` | Settings file to use |
| `DB_NAME` | `finance_db` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | `postgres` | PostgreSQL password |
| `DB_HOST` | `db` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `SENTRY_DSN` | (empty) | Sentry DSN. Leave empty for normal app behavior without Sentry |

## Response Format

All API responses follow a consistent envelope format:

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {},
    "errors": null
}
```
