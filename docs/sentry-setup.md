# Sentry Error Monitoring

Optional error monitoring via [Sentry](https://sentry.io/). Captures unhandled server errors (5xx) and sends them to your Sentry dashboard. The application runs normally when `SENTRY_DSN` is empty.

## Current Status

Sentry is already wired in `config/settings/base.py`. It only initializes when both of these are true:

- `sentry_sdk` is installed
- `SENTRY_DSN` is set

If either one is missing, the application still starts and runs normally. The middleware in `core/middleware.py` also handles the missing package safely.

## How to Enable

### 1. Install the SDK

`requirements.txt` already includes the Sentry SDK:

```
sentry-sdk[django]>=2.0,<3.0
```

Then install:

```bash
pip install -r requirements.txt
```

### 2. Configuration Behavior

`config/settings/base.py` already initializes Sentry automatically when a DSN is present:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from core.exceptions import ApplicationError


def filter_sentry_events(event, hint):
    """Don't send expected 4xx errors to Sentry. Only 5xx / unhandled."""
    if "exc_info" in hint:
        exc = hint["exc_info"][1]
        if isinstance(exc, ApplicationError):
            return None
    return event


SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

if sentry_sdk and SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(
                level=logging.WARNING,
                event_level=logging.ERROR,
            ),
        ],
        environment=os.environ.get("DJANGO_ENV", "development"),
        traces_sample_rate=0.1,
        send_default_pii=False,
        before_send=filter_sentry_events,
    )
```

### 3. Set Environment Variable

```bash
export SENTRY_DSN=https://your-key@sentry.io/your-project-id
```

Or in `.env`:
```
SENTRY_DSN=https://your-key@sentry.io/your-project-id
```

For Docker, add it to `docker-compose.yml` under `web.environment`.

### 4. Result

- No `SENTRY_DSN`: app works normally and sends nothing to Sentry
- Valid `SENTRY_DSN`: unhandled server errors and configured logs are sent to Sentry

## What Gets Sent to Sentry

| Event Type | Sent? | Reason |
|------------|-------|--------|
| Unhandled 5xx errors | Yes | Server bugs that need fixing |
| `ApplicationError` subclasses (4xx) | No | Expected business errors (validation, permissions, not found) |
| Django WARNING+ logs | Yes | Via `LoggingIntegration` |

### Event Filtering

The `filter_sentry_events` function intercepts all events before sending. Any exception that inherits from `ApplicationError` (defined in `core/exceptions.py`) is silently dropped. This includes:

- `ValidationError` (400)
- `PermissionDeniedError` (403)
- `NotFoundError` (404)
- `ConflictError` (409)

## User Context Middleware

`core/middleware.py` contains `SentryUserContextMiddleware` which attaches the authenticated user's info to every Sentry event:

```python
sentry_sdk.set_user({
    "id": request.user.id,
    "email": request.user.email,
    "role": request.user.role,
})
```

This means every error in Sentry shows which user triggered it and their role. The middleware is safe to leave enabled even when Sentry is disabled — it checks for the package first.

## Configuration Reference

| Setting | Value | Description |
|---------|-------|-------------|
| `traces_sample_rate` | `0.1` | 10% of requests get performance tracing |
| `send_default_pii` | `False` | No personal data in breadcrumbs |
| `environment` | From `DJANGO_ENV` env var | Tags events as development/production |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | (empty) | Sentry project DSN. Leave empty to disable |
| `DJANGO_ENV` | `development` | Environment tag for Sentry events |
