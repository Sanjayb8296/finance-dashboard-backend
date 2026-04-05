# Dashboard Module

Analytics endpoints providing financial summaries, trends, and breakdowns using database-level aggregations.

## Directory Structure

```
dashboard/
├── __init__.py
├── apps.py
├── selectors/
│   ├── __init__.py
│   └── dashboard_selector.py  # DB aggregations (Sum, Avg, Count, Max, TruncMonth)
├── services/
│   └── __init__.py            # Empty — this module is read-only
├── api/
│   ├── __init__.py
│   ├── serializers.py         # Summary, TrendItem, CategoryBreakdownItem
│   ├── views.py               # 4 view classes, one per endpoint
│   └── urls.py                # 4 URL patterns
└── tests/
    ├── __init__.py
    └── test_api.py            # 8 tests — access control, aggregations, scoping
```

## Responsibilities

- Financial summary (totals, averages, extremes)
- Monthly income/expense trends
- Category-wise breakdown with percentages
- Recent transactions
- All computations use Django ORM aggregations (`Sum`, `Avg`, `Count`, `Max`, `TruncMonth`) — no Python-level loops

## Architecture

This module has **no models and no services**. It is read-only and uses selectors directly.

```
View → Selector (DB aggregations) → FinancialRecord model
```

## Files

| File | Purpose |
|------|---------|
| `selectors/dashboard_selector.py` | `get_summary`, `get_trends`, `get_category_breakdown`, `get_recent_transactions` — all use `annotate()`/`aggregate()` |
| `api/serializers.py` | `DashboardSummarySerializer`, `TrendItemSerializer`, `CategoryBreakdownItemSerializer` |
| `api/views.py` | 4 view classes, one per endpoint |
| `api/urls.py` | 4 URL patterns |

## API Endpoints

All routes are prefixed with `/api/v1/`.

| Method | Path | Access | Description |
|--------|------|--------|-------------|
| GET | `/dashboard/summary/` | All authenticated | Total income, expense, net balance, record count, avg, largest |
| GET | `/dashboard/trends/` | All authenticated | Monthly income/expense over N months (default 12) |
| GET | `/dashboard/category-breakdown/` | All authenticated | Per-category totals with percentages |
| GET | `/dashboard/recent/` | All authenticated | N most recent transactions (default 10) |

## Role-Based Scoping

Dashboard selectors reuse the same role-based scoping as records:
- **Managers** see aggregations over their own records only
- **All other roles** see aggregations over all records

## Query Parameters

| Endpoint | Parameter | Default | Description |
|----------|-----------|---------|-------------|
| `summary` | `date_from` | — | Filter start date |
| `summary` | `date_to` | — | Filter end date |
| `trends` | `months` | 12 | Number of months to show |
| `category-breakdown` | `type` | — | Filter by income/expense |
| `category-breakdown` | `date_from` | — | Filter start date |
| `category-breakdown` | `date_to` | — | Filter end date |
| `recent` | `limit` | 10 | Number of transactions |

## Testing

- `test_api.py` — 8 tests: access control, correct aggregation totals, manager scoping, date filtering, empty dataset handling

## Links to Other Modules

- **records/** — Queries `FinancialRecord` model directly for all aggregations; shares the same role-scoping logic
- **users/** — Reads `request.user.role` to determine data scoping (managers vs. other roles)
- **core/** — Uses `StandardPagination` for the recent transactions endpoint; inherits response envelope from `ApiRenderer`
- **config/** — Registered in `INSTALLED_APPS`; routes included via `dashboard.api.urls` in `config/urls.py`
