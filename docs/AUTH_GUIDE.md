# Authentication Guide — Amoozeshyar API

This document explains how authentication works in the Amoozeshyar panel, where the code lives, and how to test every auth endpoint in **Postman**.

---

## Overview

Amoozeshyar uses a **custom auth system** (not Django’s built-in `User` model). It is built on three database models:

| Model | Purpose |
|-------|---------|
| `AuthAccount` | Login username, email, password hash, link to `Person` |
| `AuthRole` | Roles: `admin`, `staff`, `student`, `teacher`, `employee` |
| `AuthSession` | Server-side session token with expiry (default **7 days**) |

After login you receive a **token** (`session_key`). Send it on every protected request:

```http
Authorization: Token <session_key>
```

**Important:** The word `Token` followed by a space is required. Sending only the raw key without the `Token ` prefix is rejected:

```http
# Wrong — will NOT work
Authorization: d450756c0669a93a108635ec7b352c760ac24f8f14855267cbcd4a9efe9496f9

# Correct
Authorization: Token d450756c0669a93a108635ec7b352c760ac24f8f14855267cbcd4a9efe9496f9
```

If you send an `Authorization` header (even a wrong one), the API **will not** fall back to the Django session cookie. Cookie-based auth only applies when **no** `Authorization` header is present (e.g. same-origin browser requests without a token header).

There is also an optional **Django session cookie** (`sessionid`) set at login — useful for browser/frontend, but **Postman normally uses the Token header**.

```mermaid
sequenceDiagram
    participant Client as Postman_or_Frontend
    participant API as Django_API
    participant DB as Database

    Client->>API: POST /api/v1/auth/login/ {username, password}
    API->>DB: Verify AuthAccount password
    API->>DB: Create AuthSession (session_key, expires_at)
    API->>Client: {token, expires_at, account}
    Client->>API: GET /api/v1/auth/me/ + Authorization Token
    API->>DB: Lookup AuthSession by token
    API->>Client: {account, person, student, ...}
    Client->>API: POST /api/v1/auth/logout/ + Authorization Token
    API->>DB: Delete AuthSession
    API->>Client: {detail: logged out}
```

---

## File map

| File | Role |
|------|------|
| [`core/models.py`](../core/models.py) | `AuthRole`, `AuthAccount`, `AuthSession`, `AuthAccountRole` models |
| [`core/api/authentication.py`](../core/api/authentication.py) | Token + Session authentication classes, `create_auth_session()` |
| [`core/api/permissions.py`](../core/api/permissions.py) | Role-based permissions (`IsAuthenticatedAccount`, `IsAdminRole`, …) |
| [`core/api/views/auth.py`](../core/api/views/auth.py) | Login, Logout, Me, Password Reset views |
| [`core/api/serializers/auth.py`](../core/api/serializers/auth.py) | Request/response serializers |
| [`core/api/urls.py`](../core/api/urls.py) | Auth URL routes under `/api/v1/auth/` |
| [`config/settings.py`](../config/settings.py) | `REST_FRAMEWORK` default auth & permissions |
| [`core/static/amoozeshyar/auth.js`](../core/static/amoozeshyar/auth.js) | Frontend login/logout (localStorage token) |
| [`core/page_views.py`](../core/page_views.py) | `/logout/` page (clears session + calls API) |
| [`core/management/commands/seed_api_demo.py`](../core/management/commands/seed_api_demo.py) | Creates demo user for testing |
| [`core/api/tests.py`](../core/api/tests.py) | Automated login/me tests |

OpenAPI docs (interactive): [Swagger](http://127.0.0.1:8000/api/docs/) · [ReDoc](http://127.0.0.1:8000/api/redoc/)

---

## Auth endpoints

Base URL (local): `http://127.0.0.1:8000`

| Endpoint | Method | Auth required? | Description |
|----------|--------|----------------|-------------|
| `/api/v1/auth/login/` | POST | No | Login, get token |
| `/api/v1/auth/logout/` | POST | Yes | Invalidate token |
| `/api/v1/auth/me/` | GET | Yes | Current user profile |
| `/api/v1/auth/password/reset/` | POST | No | Reset password via security answer |

Admin-only CRUD (separate from login flow):

| Endpoint | Description |
|----------|-------------|
| `/api/v1/auth-roles/` | Manage roles |
| `/api/v1/auth-accounts/` | Manage accounts |
| `/api/v1/auth-sessions/` | View sessions (read-only) |
| `/api/v1/auth-account-roles/` | Assign roles to accounts |

---

## Demo credentials

Create the demo user first:

```bash
python manage.py migrate
python manage.py seed_api_demo
```

| Field | Value |
|-------|-------|
| Username | `demo_student` |
| Password | `demo1234` |
| Role | `student` |
| Student number | `1400123456` |

Django admin (separate from API auth):

| Username | Password |
|----------|----------|
| `admin` | `root@!123` |

---

## How login works (code flow)

1. Client sends `username` + `password` to `LoginAPIView`.
2. Server looks up `AuthAccount` by username and checks `password_hash`.
3. Fallback: if no account, checks legacy `Person.password` and linked `auth_account`.
4. If `person.account_locked` → **403**.
5. On success:
   - Creates `AuthSession` with random 64-char hex token (7-day expiry).
   - Stores `auth_account_id` in Django session cookie.
   - Returns `token`, `expires_at`, `account` (with `role_codes`).

Relevant code:

```python
# core/api/views/auth.py — simplified
session = create_auth_session(account, request)
request.session["auth_account_id"] = str(account.pk)
return Response({
    "token": session.session_key,
    "expires_at": session.expires_at,
    "account": AuthAccountSerializer(account).data,
})
```

Token validation (`AuthSessionTokenAuthentication`):

```python
# core/api/authentication.py — simplified
session = AuthSession.objects.filter(
    session_key=token,
    expires_at__gt=timezone.now(),
).select_related("account", "account__person").first()
if not session:
    raise AuthenticationFailed("توکن نامعتبر یا منقضی شده است.")
return AuthUser(session.account), token
```

---

## Postman setup

### 1. Create an environment (recommended)

| Variable | Initial value |
|----------|---------------|
| `base_url` | `http://127.0.0.1:8000` |
| `token` | *(empty — filled after login)* |

Use `{{base_url}}` and `{{token}}` in requests below.

### 2. Login — get token

**Request**

```
POST {{base_url}}/api/v1/auth/login/
```

**Headers**

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |

**Body** (raw JSON)

```json
{
  "username": "demo_student",
  "password": "demo1234"
}
```

**Success response — `200 OK`**

```json
{
  "token": "a1b2c3d4e5f6...64 hex characters...",
  "expires_at": "2026-06-22T21:00:00+03:30",
  "account": {
    "id": "uuid-here",
    "person": "uuid-here",
    "person_name": "دانشجو نمونه",
    "username": "demo_student",
    "email": "demo@ntbiau.ac.ir",
    "role_codes": ["student"]
  }
}
```

**Postman tip:** In the login request **Tests** tab, save the token automatically:

```javascript
if (pm.response.code === 200) {
  const json = pm.response.json();
  pm.environment.set("token", json.token);
}
```

**Error responses**

| Status | Body | Cause |
|--------|------|-------|
| `401` | `{"detail": "نام کاربری یا رمز عبور اشتباه است."}` | Wrong username/password |
| `403` | `{"detail": "حساب کاربری قفل شده است."}` | Account locked |
| `400` | Field validation errors | Missing username/password |

---

### 3. Get current user — `/me`

**Request**

```
GET {{base_url}}/api/v1/auth/me/
```

**Headers**

| Key | Value |
|-----|-------|
| `Authorization` | `Token {{token}}` |

**Success response — `200 OK`**

```json
{
  "account": {
    "id": "...",
    "username": "demo_student",
    "email": "demo@ntbiau.ac.ir",
    "role_codes": ["student"],
    "person_name": "دانشجو نمونه"
  },
  "person": {
    "id": "...",
    "username": "demo_student",
    "full_name": "دانشجو نمونه",
    "national_code": "0012345678"
  },
  "student": {
    "id": "...",
    "student_number": "1400123456",
    "gpa": null
  },
  "teacher": null,
  "employee": null
}
```

**Without token → `403 Forbidden`**

---

### 4. Logout

**Request**

```
POST {{base_url}}/api/v1/auth/logout/
```

**Headers**

| Key | Value |
|-----|-------|
| `Authorization` | `Token {{token}}` |

**Body:** none

**Success response — `200 OK`**

```json
{
  "detail": "با موفقیت خارج شدید."
}
```

After logout, the same token no longer works on `/me/` → `401`.

---

### 5. Password reset

Requires `Person.security_question` and `Person.security_answer` to be set in the database (demo user may not have these — set via admin if testing).

**Request**

```
POST {{base_url}}/api/v1/auth/password/reset/
```

**Body** (raw JSON)

```json
{
  "username": "demo_student",
  "security_answer": "your-answer",
  "new_password": "newpass123"
}
```

**Success — `200 OK`**

```json
{
  "detail": "رمز عبور با موفقیت تغییر کرد."
}
```

| Status | Cause |
|--------|-------|
| `404` | User not found |
| `400` | Wrong security answer |
| `400` | `new_password` shorter than 6 characters |

---

### 6. Test a protected API endpoint

Any endpoint except `/api/ping/` and auth login/reset requires the token.

**Example — dashboard composite API**

```
GET {{base_url}}/api/v1/pages/dashboard/
Authorization: Token {{token}}
```

**Example — list const values**

```
GET {{base_url}}/api/v1/const-values/
Authorization: Token {{token}}
```

Without token → `403`.

---

## Postman collection (quick import)

You can create a collection with these 4 requests:

1. **Login** — POST `/api/v1/auth/login/` → save `token` to environment  
2. **Me** — GET `/api/v1/auth/me/` → uses `{{token}}`  
3. **Dashboard** — GET `/api/v1/pages/dashboard/` → uses `{{token}}`  
4. **Logout** — POST `/api/v1/auth/logout/` → uses `{{token}}`

---

## Permissions by role

Defined in [`core/api/permissions.py`](../core/api/permissions.py):

| Permission class | Who passes |
|------------------|------------|
| `IsAuthenticatedAccount` | Any logged-in user |
| `IsAdminRole` | Role code `admin` |
| `IsStudentRole` | Role code `student` |
| `AdminWriteAuthenticatedRead` | All authenticated can GET; only `admin`/`staff` can POST/PUT/DELETE |
| `IsOwnerStudentOrStaff` | Student sees own records; staff/admin see all |

Default for all API views (in `settings.py`):

```python
'DEFAULT_PERMISSION_CLASSES': [
    'core.api.permissions.IsAuthenticatedAccount',
],
```

Public endpoints override this with `permission_classes = [AllowAny]` (login, password reset, ping).

---

## Frontend auth (browser)

The student panel uses [`core/static/amoozeshyar/auth.js`](../core/static/amoozeshyar/auth.js):

1. **Login page** calls `POST /api/v1/auth/login/` and stores token in `localStorage`.
2. **Protected pages** call `requireAuth()` — redirects to `/` if no token.
3. **Logout** goes to `/logout/` which clears Django session and calls `logout()` to invalidate the API token.

```javascript
// Stored keys in localStorage
amoozeshyar_token
amoozeshyar_token_expires
amoozeshyar_account

// Header sent on API calls
Authorization: Token <token from localStorage>
```

---

## cURL examples (same as Postman)

**Login**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_student","password":"demo1234"}'
```

**Me** (replace `YOUR_TOKEN`)

```bash
curl http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Logout**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/logout/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `403` on all endpoints | Missing or wrong `Authorization` header. Format must be **`Token <key>`** (capital T, one space, then the key). |
| `403` with raw token (no `Token ` prefix) | Add the `Token ` prefix before the session key. |
| `403` / invalid token message | Token expired (7 days) or logged out. Login again. |
| `401` wrong password | Run `seed_api_demo` or check username in Django admin → Auth accounts. |
| `demo_student` not found | Run `python manage.py seed_api_demo` |
| CSRF errors in browser only | API uses token auth; CSRF applies to session forms, not Token header requests. |
| Password reset fails | Set `security_question` / `security_answer` on the Person record first. |

---

## Run automated auth tests

```bash
python manage.py test core.api.tests.APISmokeTests.test_login_and_me
```

Or all API tests:

```bash
python manage.py test core.api
```

---

## Related docs

- [README.md](../README.md) — project setup (Persian)
- [/api/docs/](http://127.0.0.1:8000/api/docs/) — Swagger UI with live schemas
- [/docs/django-admin/](http://127.0.0.1:8000/docs/django-admin/) — Django admin guide
