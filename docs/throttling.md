# Role-Based Throttling

API rate limiting that adjusts based on the authenticated user's role.

## How It Works

The custom `RoleBasedThrottle` class in `core/throttling.py` checks `request.user.role` and applies a different rate limit for each role. Anonymous requests get the lowest limit.

```
Request → Authenticate → Check role → Apply rate limit → Allow or 429
```

## Rate Limits

| Role | Rate | Requests/Hour |
|------|------|---------------|
|Viewer | `100/hour` | 100    |
|Analyst| `200/hour` | 200    |
|Manager| `300/hour` | 300    |
|Admin  | `500/hour` | 500    |
|Auditor| `200/hour` | 200    |
|Anonymous| `30/hour`| 30     |

Rates are configured in `config/settings/base.py` under `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`.

## Configuration

```python
# config/settings/base.py

REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "core.throttling.RoleBasedThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "viewer": "100/hour",
        "analyst": "200/hour",
        "manager": "300/hour",
        "admin": "500/hour",
        "auditor": "200/hour",
        "anon": "30/hour",
    },
}
```

## Development Override

Throttling is **disabled** in development to avoid hitting limits during testing:

```python
# config/settings/development.py
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
```

## Throttle Response

When a user exceeds their rate limit, the API returns:

```json
{
    "success": false,
    "message": "Request was throttled. Expected available in 1800 seconds.",
    "data": null,
    "errors": null
}
```

HTTP status: `429 Too Many Requests`

## Implementation

The `RoleBasedThrottle` class extends DRF's `SimpleRateThrottle`:

1. For authenticated users: uses `role` as the throttle scope (e.g., `"admin"`)
2. For anonymous users: falls back to `"anon"` scope
3. Cache key includes the user ID, so limits are per-user

The rate string (e.g., `"500/hour"`) is resolved from `DEFAULT_THROTTLE_RATES` using the role name as the key.
