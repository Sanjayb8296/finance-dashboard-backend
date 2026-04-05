# JWT Authentication

Token-based authentication using [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/).

## How It Works

```
Client                          Server
  │                                │
  ├── POST /auth/login/ ──────────►│  Verify email + password
  │◄── { access, refresh } ────────┤  Return token pair
  │                                │
  ├── GET /records/ ───────────────►│  Validate access token
  │   Authorization: Bearer <access>│
  │◄── { data } ───────────────────┤
  │                                │
  │  ... access token expires ...  │
  │                                │
  ├── POST /auth/refresh/ ─────────►│  Validate refresh token
  │   { refresh: <token> }         │
  │◄── { access, refresh } ────────┤  New pair (old refresh blacklisted)
  │                                │
  ├── POST /auth/logout/ ──────────►│  Blacklist refresh token
  │   { refresh: <token> }         │
  │◄── 200 OK ─────────────────────┤
```

## Token Lifetimes

| Token | Lifetime | Purpose |
|-------|----------|---------|
| Access | 30 minutes | Short-lived, sent with every request |
| Refresh | 7 days | Long-lived, used only to get new access tokens |

## Configuration

In `config/settings/base.py`:

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

### Key Settings

| Setting | Value | Effect |
|---------|-------|--------|
| `ROTATE_REFRESH_TOKENS` | `True` | Every refresh returns a new refresh token |
| `BLACKLIST_AFTER_ROTATION` | `True` | Old refresh tokens can't be reused |
| `AUTH_HEADER_TYPES` | `Bearer` | Requests use `Authorization: Bearer <token>` |

## Auth Endpoints

All under `/api/v1/auth/`.

### Register — `POST /auth/register/`

Creates a new user with the VIEWER role (default).

```json
// Request
{ "email": "user@example.com", "password": "securepass123", "first_name": "John", "last_name": "Doe" }

// Response
{ "success": true, "data": { "user": {...}, "tokens": { "access": "...", "refresh": "..." } } }
```

### Login — `POST /auth/login/`

Returns a JWT token pair.

```json
// Request
{ "email": "admin@example.com", "password": "admin123!" }

// Response
{ "success": true, "data": { "user": {...}, "tokens": { "access": "eyJ...", "refresh": "eyJ..." } } }
```

### Refresh — `POST /auth/refresh/`

Exchanges a refresh token for a new token pair.

```json
// Request
{ "refresh": "eyJ..." }

// Response
{ "success": true, "data": { "access": "eyJ...", "refresh": "eyJ..." } }
```

### Logout — `POST /auth/logout/`

Blacklists the refresh token so it can no longer be used.

```json
// Request (requires Bearer token in header)
{ "refresh": "eyJ..." }

// Response
{ "success": true, "message": "Successfully logged out" }
```

## Using Tokens in Requests

Include the access token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

All endpoints except register, login, refresh, and health check require this header.

## Token Blacklisting

The project uses `rest_framework_simplejwt.token_blacklist` (registered in `INSTALLED_APPS`). This stores invalidated refresh tokens in the database to prevent reuse after:

- **Logout**: Explicitly blacklisted by the user
- **Rotation**: Automatically blacklisted when a new refresh token is issued

## Security Notes

- Access tokens are stateless — they cannot be revoked before expiry
- Refresh tokens are checked against the blacklist on every use
- Deactivated users (`is_active=False`) are rejected at login, even with valid tokens
- Passwords are validated against Django's 4 built-in validators (similarity, minimum length, common passwords, numeric)
