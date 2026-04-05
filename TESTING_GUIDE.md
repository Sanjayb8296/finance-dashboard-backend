# Setup And API Testing Guide

This guide explains how to run the project locally, seed sample data, and test the available API endpoints.

## Prerequisites

- Python 3.11 or later
- `pip`
- Optional: virtual environment support

## Project Setup

From the project root:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

If the server starts successfully, the API will usually be available at:

```text
http://127.0.0.1:8000/
```

## Sample Seeded Credentials

After running `python manage.py seed_data`, the following demo users are available:

- `admin@example.com` / `admin123!`
- `manager@example.com` / `manager123!`
- `analyst@example.com` / `analyst123!`
- `viewer@example.com` / `viewer123!`
- `auditor@example.com` / `auditor123!`

## API Documentation URLs

Once the server is running:

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

## Recommended Testing Method

The easiest way to test the endpoints is through Swagger UI.

### Step 1: Open Swagger

Open:

```text
http://127.0.0.1:8000/api/docs/
```

### Step 2: Login

Use the `POST /api/v1/auth/login/` endpoint with one of the seeded accounts.

Example request body:

```json
{
  "email": "admin@example.com",
  "password": "admin123!"
}
```

The response will return:

- `access`
- `refresh`
- user details

### Step 3: Authorize Swagger

1. Copy the `access` token from the login response.
2. Click the `Authorize` button in Swagger.
3. Enter:

```text
Bearer <your_access_token>
```

4. Submit the authorization dialog.

You can now test protected endpoints.

## Suggested Endpoint Testing Order

### Authentication

- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/refresh/`
- `POST /api/v1/auth/logout/`

### Current User

- `GET /api/v1/users/me/`
- `PATCH /api/v1/users/me/`

### Dashboard

- `GET /api/v1/dashboard/summary/`
- `GET /api/v1/dashboard/trends/`
- `GET /api/v1/dashboard/category-breakdown/`
- `GET /api/v1/dashboard/recent/`

### Records

- `GET /api/v1/records/`
- `POST /api/v1/records/`
- `GET /api/v1/records/{id}/`
- `PATCH /api/v1/records/{id}/`
- `DELETE /api/v1/records/{id}/`
- `GET /api/v1/records/export/`
- `POST /api/v1/records/bulk/`

### Audit

- `GET /api/v1/audit/logs/`
- `GET /api/v1/audit/logs/{id}/`

### Health

- `GET /api/v1/health/`

## Role-Based Testing Guide

Use different seeded users to verify permissions.

### Viewer

Expected capabilities:

- can log in
- can access own profile
- can access dashboard endpoints
- cannot create or modify records
- cannot access user management
- cannot access audit logs

### Analyst

Expected capabilities:

- can view records
- can export records
- can access dashboard endpoints
- cannot create or modify records

### Manager

Expected capabilities:

- can create records
- can update and delete only their own records
- can list records scoped to their own data
- can access dashboard endpoints

### Admin

Expected capabilities:

- full user management
- full record management
- bulk record creation
- access to audit logs
- access to all dashboard endpoints

### Auditor

Expected capabilities:

- can read audit logs
- can list users
- can view records
- cannot create or modify records

## Testing In Postman

You can also test using Postman.

### Login First

Send:

```http
POST /api/v1/auth/login/
```

With body:

```json
{
  "email": "admin@example.com",
  "password": "admin123!"
}
```

Copy the returned `access` token.

### Add Authorization Header

For protected endpoints, add:

```text
Authorization: Bearer <access_token>
```

### Example Record Creation Request

```http
POST /api/v1/records/
```

```json
{
  "amount": "5000.00",
  "type": "income",
  "category": "salary",
  "date": "2026-04-05",
  "description": "Monthly salary"
}
```

Use `admin` or `manager` credentials for this request.

## Running Automated Tests

To run the test suite:

```bash
pytest
```

Or on Windows with the local virtual environment:

```bash
venv\Scripts\pytest.exe -q
```

## Common Issues

### Unauthorized Or Forbidden Responses

- Make sure you logged in first
- Make sure the token was added as `Bearer <token>`
- Check whether the selected user role is allowed to access that endpoint

### No Sample Data Visible

- Ensure migrations were applied
- Run `python manage.py seed_data`

### Swagger Is Not Opening

- Confirm the server is still running
- Check that you are visiting `http://127.0.0.1:8000/api/docs/`

## Notes

- Sentry configuration is optional and should be enabled only through environment variables.
- The seeded data is intended for local testing and demonstration only.
