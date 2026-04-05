# Swagger / OpenAPI Setup

Interactive API documentation powered by [drf-spectacular](https://drf-spectacular.readthedocs.io/) (OpenAPI 3.0).

## Accessing the Docs

| URL | Interface | Description |
|-----|-----------|-------------|
| `/api/docs/` | Swagger UI | Interactive API explorer with "Try it out" |
| `/api/redoc/` | ReDoc | Clean, readable API reference |
| `/api/schema/` | JSON Schema | Raw OpenAPI 3.0 spec (for code generators) |

## Authentication in Swagger UI

1. Login via `POST /api/v1/auth/login/` with email + password
2. Copy the `access` token from the response
3. Click the **Authorize** button (lock icon) at the top
4. Enter: `Bearer <your-access-token>`
5. All subsequent requests will include the JWT header

## Configuration

Settings are in `config/settings/base.py` under `SPECTACULAR_SETTINGS`:

```python
SPECTACULAR_SETTINGS = {
    "TITLE": "Finance Dashboard API",
    "DESCRIPTION": "Backend API for finance data processing and access control system.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SECURITY": [{"BearerAuth": []}],
    "COMPONENT_SPLIT_REQUEST": True,
}
```

### Key Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `SERVE_INCLUDE_SCHEMA` | `False` | Hides the schema endpoint from the docs |
| `COMPONENT_SPLIT_REQUEST` | `True` | Separates request/response serializers in the schema |
| `SECURITY` | `BearerAuth` | Adds JWT auth to all endpoints by default |
| `ENUM_NAME_OVERRIDES` | Role, RecordType, Category | Clean enum names in the schema |

### Tag Groups

Endpoints are organized into 6 groups:

| Tag | Endpoints |
|-----|-----------|
| Auth | Register, Login, Refresh, Logout |
| Users | Profile, User CRUD |
| Records | Financial record CRUD, Export, Bulk |
| Dashboard | Summary, Trends, Category Breakdown, Recent |
| Audit | Audit log list and detail |
| System | Health check |

## Schema Decorators

Every view uses `@extend_schema` to provide accurate request/response types:

```python
from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=["Records"],
    request=RecordCreateSerializer,
    responses={201: RecordOutputSerializer},
)
def post(self, request):
    ...
```

### Common Patterns Used

| Pattern | Example | Used For |
|---------|---------|----------|
| `request=SerializerClass` | `request=LoginSerializer` | Define request body |
| `responses={200: Serializer}` | `responses={200: RecordOutputSerializer}` | Define success response |
| `responses={200: None}` | Logout, Delete | No response body |
| `inline_serializer(...)` | Refresh, Health | One-off response shapes |
| `OpenApiTypes.BINARY` | CSV export | File download responses |
| `OpenApiParameter(...)` | Filters, pagination | Query parameter docs |

## URL Configuration

Defined in `config/urls.py`:

```python
path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
```

Note: Documentation URLs are at `/api/docs/` and `/api/redoc/`, not under `/api/v1/`.
