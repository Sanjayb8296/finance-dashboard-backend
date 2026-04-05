# Audit Module

Immutable audit trail recording all significant actions in the system.

## Directory Structure

```
audit/
├── __init__.py
├── admin.py
├── apps.py
├── models/
│   ├── __init__.py
│   └── audit_log.py           # AuditLog model, AuditAction enum
├── services/
│   ├── __init__.py
│   └── audit_service.py       # log() — creates entries; get_client_ip()
├── selectors/
│   ├── __init__.py
│   └── audit_selector.py      # get_audit_logs (filtered), get_audit_log_by_id
├── api/
│   ├── __init__.py
│   ├── serializers.py         # AuditLogOutputSerializer
│   ├── views.py               # AuditLogListView, AuditLogDetailView
│   └── urls.py                # 2 URL patterns
├── migrations/
│   ├── __init__.py
│   ├── 0001_initial.py
│   └── 0002_initial.py
└── tests/
    ├── __init__.py
    └── test_api.py            # 8 tests — permissions, detail view, 404 handling
```

## Responsibilities

- `AuditLog` model storing who did what, when, and what changed
- Audit service called by other modules' services (records, users)
- Read-only API for admins and auditors
- Filtering by action, resource type, user, and date range

## Architecture

```
Other services call audit_service.log() → AuditLog created
Admin/Auditor → View → Selector → AuditLog model
```

Audit logs are **write-once, read-only**. There are no update or delete endpoints.

## Files

| File | Purpose |
|------|---------|
| `models/audit_log.py` | `AuditLog` model with user, action, resource_type, resource_id, changes (JSON), ip_address, timestamp. `AuditAction` enum (create, update, delete, restore, login, logout, etc.) |
| `services/audit_service.py` | `log()` — creates audit entries. `get_client_ip()` — extracts IP from request |
| `selectors/audit_selector.py` | `get_audit_logs` (filtered), `get_audit_log_by_id` |
| `api/serializers.py` | `AuditLogOutputSerializer` |
| `api/views.py` | `AuditLogListView`, `AuditLogDetailView` |
| `api/urls.py` | 2 URL patterns |

## API Endpoints

All routes are prefixed with `/api/v1/`.

| Method | Path | Access | Description |
|--------|------|--------|-------------|
| GET | `/audit/logs/` | Admin, Auditor | List audit logs (paginated, filtered) |
| GET | `/audit/logs/{id}/` | Admin, Auditor | Audit log detail |

## What Gets Logged

The records service logs these actions automatically:

| Action | Trigger | Changes Field |
|--------|---------|---------------|
| **CREATE** | Financial record created | — |
| **UPDATE** | Financial record updated | Old/new values as JSON |
| **DELETE** | Financial record soft-deleted | — |
| **Bulk CREATE** | Records bulk-created | Record count |

## Testing

- `test_api.py` — 8 tests: permission checks (admin/auditor can access, others cannot), detail view, 404 handling
- Integration tests: verify that record CRUD operations automatically create audit log entries

## Links to Other Modules

- **records/** — `record_service` calls `audit_service.log()` on every create, update, delete, and bulk create operation
- **users/** — `AuditLog.user` FK to `User`; views use `IsAdminOrAuditor` permission from `users.permissions`
- **core/** — Uses response envelope via `ApiRenderer`; raises `NotFoundError` for missing logs
- **config/** — Registered in `INSTALLED_APPS`; routes included via `audit.api.urls` in `config/urls.py`
