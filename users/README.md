# Users Module

Handles authentication, user management, and the role-based access control system.

## Directory Structure

```
users/
├── __init__.py
├── admin.py
├── apps.py
├── models/
│   ├── __init__.py
│   └── user.py                # User model, Role enum, UserManager
├── services/
│   ├── __init__.py
│   └── user_service.py        # Register, auth, CRUD, profile logic
├── selectors/
│   ├── __init__.py
│   └── user_selector.py       # User queries with filtering
├── permissions/
│   ├── __init__.py
│   └── user_permissions.py    # IsAdmin, IsAdminOrAuditor
├── api/
│   ├── __init__.py
│   ├── serializers.py         # Input/output serializers
│   ├── views.py               # Auth + user management views
│   └── urls.py                # /auth/ and /users/ routes
├── management/
│   └── commands/
│       └── seed_data.py       # Creates 5 users + ~180 financial records
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py
└── tests/
    ├── __init__.py
    ├── test_api.py            # 17 tests — endpoints + permission matrix
    └── test_services.py       # 10 tests — registration, auth, CRUD, edge cases
```

## Responsibilities

- Custom `User` model with email-based auth (no username)
- 5-role RBAC system: VIEWER, ANALYST, MANAGER, ADMIN, AUDITOR
- JWT authentication (access + refresh tokens, blacklisting on logout)
- User registration (self-service, defaults to VIEWER)
- User CRUD (admin only)
- Profile management (self-service, name only)
- Permission classes reused across all modules

## Request Flow

```
View (permission check) → Service (business logic) → Selector (queries) → Model
```

## Files

| File | Purpose |
|------|---------|
| `models/user.py` | `User` model, `Role` enum, `UserManager` with `create_user`/`create_superuser` |
| `services/user_service.py` | `register_user`, `authenticate_user`, `create_user`, `update_user`, `deactivate_user`, `update_profile` |
| `selectors/user_selector.py` | `get_users` (with filtering), `get_user_by_id` |
| `permissions/user_permissions.py` | `IsAdmin`, `IsAdminOrAuditor` — reused by records and audit modules |
| `api/serializers.py` | Input: Register, Login, Refresh, UserCreate, UserUpdate, ProfileUpdate. Output: UserOutput, UserMinimal, LoginOutput |
| `api/views.py` | Register, Login, Refresh, Logout, Profile, UserListCreate, UserDetail |
| `api/urls.py` | Auth routes under `/auth/`, user management under `/users/` |
| `management/commands/seed_data.py` | Creates 5 users (one per role) + ~180 financial records for testing |

## API Endpoints

All routes are prefixed with `/api/v1/`.

| Method | Path | Access | Description |
|--------|------|--------|-------------|
| POST | `/auth/register/` | Public | Register with VIEWER role |
| POST | `/auth/login/` | Public | Returns JWT access + refresh tokens |
| POST | `/auth/refresh/` | Public | Rotate access token |
| POST | `/auth/logout/` | Authenticated | Blacklist refresh token |
| GET | `/users/me/` | Authenticated | Own profile |
| PATCH | `/users/me/` | Authenticated | Update own name |
| GET | `/users/` | Admin, Auditor | List users (filterable by role, is_active, search) |
| POST | `/users/` | Admin | Create user with any role |
| GET | `/users/{id}/` | Admin, Auditor | User detail |
| PATCH | `/users/{id}/` | Admin | Update name, role, is_active |
| DELETE | `/users/{id}/` | Admin | Deactivate user (soft) |

## Key Business Rules

- Admins cannot demote themselves
- Admins cannot deactivate themselves
- Last admin cannot be deactivated
- Duplicate emails are rejected (409 Conflict)
- Deactivated users cannot log in

## Testing

- `test_services.py` — 10 tests covering registration, auth, user CRUD, edge cases
- `test_api.py` — 17 tests covering all endpoints and permission matrix

## Links to Other Modules

- **core/** — `User` inherits from `TimestampedModel`; services raise `ConflictError`, `NotFoundError`, `PermissionDeniedError`
- **records/** — `FinancialRecord.user` is a FK to `User`; record services check `user.role` for permission guards
- **audit/** — `AuditLog.user` references the acting user
- **dashboard/** — Dashboard selectors scope data based on `user.role` (managers see only their own records)
- **config/** — Permission classes (`IsAdmin`, `IsAdminOrAuditor`) are referenced by records and audit views
