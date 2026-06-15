# Amoozeshyar Panel (NTBIAU)

Welcome to the **Amoozeshyar** university management panel. This project is built with Django and exposes a full REST API documented via OpenAPI (Swagger UI and ReDoc).

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Sepahkar/SD.NTB.1404.05.2.git
cd SD.NTB.1404.05.2
```

### 2. Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 3. Database & Server

```bash
python manage.py migrate
python manage.py seed_api_demo   # optional demo user
python manage.py runserver
```

Server: `http://127.0.0.1:8000/`

---

## Administrative Access

| Item | Value |
|------|-------|
| Admin URL | `http://127.0.0.1:8000/admin/` |
| Username | `admin` |
| Password | `root@!123` |

Registered in Django admin (Core app): lookup and academic basics (ConstValue, Lesson, Class, Term, Student, …), plus **Books**, **Library book lendings**, **Library resources**, **Academic events**, and **Academic announcements**. Student records include an inline transcript editor.

Demo API user (after `seed_api_demo`):

| Username | Password |
|----------|----------|
| `demo_student` | `demo1234` |

---

## API Documentation

We use **drf-spectacular** to auto-generate OpenAPI 3 schemas. The DRF browsable API is disabled — use Swagger or ReDoc only.

| Path | Description |
|------|-------------|
| [`/api/schema/`](http://127.0.0.1:8000/api/schema/) | Raw OpenAPI JSON schema |
| [`/api/docs/`](http://127.0.0.1:8000/api/docs/) | **Swagger UI** — interactive explorer |
| [`/api/redoc/`](http://127.0.0.1:8000/api/redoc/) | **ReDoc** — Persian docs with tag groups |

### Health Check

`GET /api/ping/` — no authentication required.

### Authentication

```http
POST /api/v1/auth/login/
Content-Type: application/json

{"username": "demo_student", "password": "demo1234"}
```

Use the returned `token` in subsequent requests:

```http
Authorization: Token <session_key>
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login/` | POST | Login |
| `/api/v1/auth/logout/` | POST | Logout |
| `/api/v1/auth/me/` | GET | Current user profile |
| `/api/v1/auth/password/reset/` | POST | Password reset |

### API Domains (v1)

All CRUD resources are under `/api/v1/` with pagination (20/page), search, ordering, and filters.

| Tag | Resources |
|-----|-----------|
| **Authentication** | login, logout, me, password reset |
| **Auth Entities** | auth-roles, auth-accounts, auth-sessions, auth-account-roles |
| **Lookup** | const-values, departments, education-branches, tendencies, terms |
| **Person & Contact** | persons, phone-numbers, email-addresses, person-skills, postal-addresses |
| **Profiles** | teachers, students, employees, teacher-research-interests |
| **Academic** | lessons, classes, class-offers, exams, exam-results, attendances, transcripts, … |
| **Finance & Requests** | student-payments, student-requests, loans, scholarships, dormitory-requests, … |
| **Library & Misc** | books, library-book-lendings, internships, academic-events, … |
| **Composite Pages** | `/api/v1/pages/dashboard/`, `grades/`, `financial/`, … (one call per screen) |

---

## API Architecture

```
core/api/
├── authentication.py    # Token + Session auth
├── permissions.py       # Role-based access (student, admin, …)
├── pagination.py        # Standard pagination (20/page)
├── mixins.py            # Student-scoped queryset filtering
├── urls.py              # All v1 routes
├── openapi/             # Tag groups, decorators, auth schema extension
├── serializers/         # 7 serializer modules (41 entities)
├── views/               # ViewSets + auth + composite page APIs
└── tests.py             # API smoke tests
```

---

## Useful Commands

```bash
python manage.py runserver
python manage.py migrate
python manage.py seed_api_demo
python manage.py test core.api
python manage.py spectacular --file schema.yaml --validate
python manage.py createsuperuser
python manage.py check
```

---

## HTML Guides

| URL | Content |
|-----|---------|
| `/docs/` | Run & admin guide |
| `/docs/setup-theme/` | Setup and theme guide |
| `/docs/django-admin/` | Django admin complete guide |
