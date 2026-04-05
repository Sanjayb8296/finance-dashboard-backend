# Records Module

Financial record management with CRUD, role-based scoping, filtering, CSV export, and bulk creation.

## Directory Structure

```
records/
├── __init__.py
├── admin.py
├── apps.py
├── models/
│   ├── __init__.py
│   └── financial_record.py    # FinancialRecord, RecordType, Category enums
├── services/
│   ├── __init__.py
│   └── record_service.py      # CRUD + bulk create + audit logging
├── selectors/
│   ├── __init__.py
│   └── record_selector.py     # Role-scoped queries + filtering
├── permissions/
│   ├── __init__.py
│   └── record_permissions.py  # CanView, CanCreate, CanModify, CanExport
├── api/
│   ├── __init__.py
│   ├── serializers.py         # RecordCreate, RecordUpdate, BulkRecordCreate, RecordOutput
│   ├── views.py               # ListCreate, Detail, Export, BulkCreate views
│   └── urls.py                # 4 URL patterns
├── migrations/
│   ├── __init__.py
│   ├── 0001_initial.py
│   └── 0002_initial.py
└── tests/
    ├── __init__.py
    ├── test_api.py            # 16 tests — permissions, scoping, filtering, CSV export
    ├── test_services.py       # 6 tests — business logic + permission guards
    └── test_edge_cases.py     # 16 tests — validation, bulk create, response format
```

## Responsibilities

- `FinancialRecord` model with soft delete and composite indexes
- Role-scoped record access (managers see only their own)
- Create, update, soft-delete with ownership enforcement
- Filtering by type, category, date range, amount range, tags, description search
- Ordering and pagination
- CSV export
- Bulk create (admin only, up to 100 records)
- Audit trail integration (all mutations logged)

## Request Flow — 4-Layer Access Control

```
1. View permission class  → fast rejection (CanViewRecords, CanCreateRecords, etc.)
2. Service-level guard    → role check + ownership verification
3. Selector-level scoping → managers only see own records in queries
4. Object-level check     → get_record_by_id verifies ownership before returning
```

## Files

| File | Purpose |
|------|---------|
| `models/financial_record.py` | `FinancialRecord` model, `RecordType` enum (income/expense), `Category` enum (15 categories). 5 composite indexes |
| `services/record_service.py` | `create_record`, `update_record`, `soft_delete_record`, `bulk_create_records` — all with permission guards and audit logging |
| `selectors/record_selector.py` | `get_records` (role-scoped + filtered), `get_record_by_id` (object-level access check) |
| `permissions/record_permissions.py` | `CanViewRecords`, `CanCreateRecords`, `CanModifyRecords`, `CanExportRecords` |
| `api/serializers.py` | `RecordCreate`, `RecordUpdate`, `BulkRecordCreate`, `RecordOutput` |
| `api/views.py` | `RecordListCreateView`, `RecordDetailView`, `RecordExportView`, `RecordBulkCreateView` |
| `api/urls.py` | 4 URL patterns |

## API Endpoints

All routes are prefixed with `/api/v1/`.

| Method | Path | Access | Description |
|--------|------|--------|-------------|
| GET | `/records/` | Analyst, Manager, Admin, Auditor | List (paginated, filtered, role-scoped) |
| POST | `/records/` | Manager, Admin | Create record |
| GET | `/records/{id}/` | Analyst, Manager (own), Admin, Auditor | Record detail |
| PATCH | `/records/{id}/` | Manager (own), Admin | Update record |
| DELETE | `/records/{id}/` | Manager (own), Admin | Soft delete |
| GET | `/records/export/` | Analyst, Manager, Admin, Auditor | Download CSV |
| POST | `/records/bulk/` | Admin | Bulk create (max 100) |

## Role-Based Scoping

| Role | Sees | Can Modify |
|------|------|------------|
| VIEWER | Nothing | Nothing |
| ANALYST | All records | Nothing |
| MANAGER | Own records only | Own records only |
| ADMIN | All records | All records |
| AUDITOR | All records | Nothing |

## Validation

- Amount must be > 0.01 (enforced at serializer and model level)
- Type must be `income` or `expense`
- Category must be one of 15 predefined values
- Soft-deleted records are excluded from all queries by default

## Testing

- `test_api.py` — 16 tests: permissions (create/list/update/delete), scoping, filtering, CSV export
- `test_services.py` — 6 tests: service-level business logic and permission guards
- `test_edge_cases.py` — 16 tests: validation (zero/negative amounts, invalid types), bulk create, response format, health check

## Links to Other Modules

- **core/** — `FinancialRecord` inherits `TimestampedModel` + `SoftDeleteModel`; services raise `NotFoundError`, `PermissionDeniedError`
- **users/** — `FinancialRecord.user` FK to `User`; permission checks reference `users.models.Role`; views use `IsAdmin`, `IsAdminOrAuditor` from `users.permissions`
- **audit/** — `record_service` calls `audit_service.log()` on every create, update, delete, and bulk create
- **dashboard/** — Dashboard selectors query `FinancialRecord` for aggregations (shared model, separate read path)
- **config/** — Custom permissions (`CanViewRecords`, etc.) are loaded as DRF permission classes by the view layer
