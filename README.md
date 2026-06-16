# پنل آموزشیار (NTBIAU)

به **پنل مدیریت آموزشیار** خوش آمدید. این پروژه با فریم‌ورک Django ساخته شده و یک REST API کامل با مستندات OpenAPI (Swagger UI و ReDoc) در اختیار قرار می‌دهد.

---

## شروع سریع

### ۱. کلون کردن مخزن

```bash
git clone https://github.com/Sepahkar/SD.NTB.1404.05.2.git
cd SD.NTB.1404.05.2
```

### ۲. محیط مجازی

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### ۳. پایگاه داده و اجرای سرور

```bash
python manage.py migrate
python manage.py seed_api_demo   # کاربر دمو (اختیاری)
python manage.py runserver
```

آدرس سرور: `http://127.0.0.1:8000/`

---

## دسترسی مدیریتی

| مورد | مقدار |
|------|-------|
| آدرس پنل ادمین | `http://127.0.0.1:8000/admin/` |
| نام کاربری | `admin` |
| رمز عبور | `root@!123` |

**مدل‌های ثبت‌شده در Django Admin (اپ core):** داده‌های پایه و آموزشی (ConstValue، Lesson، Class، Term، Student و …)، به‌علاوه **کتاب‌ها**، **امانت کتاب**، **رزرو منابع کتابخانه**، **رویدادهای آموزشی** و **اطلاعیه‌های آموزشی**. در صفحهٔ هر دانشجو، ویرایش inline کارنامه (Transcript) نیز در دسترس است.

کاربران دمو API (پس از اجرای `seed_api_demo` — رمز همه: `demo1234`):

| نام کاربری | نقش | کاربرد |
|------------|-----|--------|
| `demo_student` | student | تست API دانشجو و صفحات composite |
| `demo_teacher` | teacher | تست API اساتید |
| `demo_staff` | staff + employee | تست عملیات staff و مراقب آزمون |
| `demo_admin` | admin | تست auth-entities و persons |

پاسخ امنیتی (password reset): `tehran`

### تست smoke API

با سرور در حال اجرا:

```bash
python manage.py seed_api_demo          # داده نمونه (idempotent)
./scripts/smoke_test_api.sh             # تست curl همه endpointها
python manage.py smoke_test_api --seed  # seeder + smoke test
python manage.py test core.api          # تست‌های Django
```

---

## مستندات API

برای تولید خودکار schemaهای OpenAPI 3 از **drf-spectacular** استفاده می‌شود. Browsable API در DRF غیرفعال است — فقط از Swagger یا ReDoc استفاده کنید.

| مسیر | توضیح |
|------|--------|
| [`/api/schema/`](http://127.0.0.1:8000/api/schema/) | schema خام JSON (OpenAPI) |
| [`/api/docs/`](http://127.0.0.1:8000/api/docs/) | **Swagger UI** — مرورگر تعاملی |
| [`/api/redoc/`](http://127.0.0.1:8000/api/redoc/) | **ReDoc** — مستندات فارسی با گروه‌بندی tag |

### بررسی سلامت سرویس

`GET /api/ping/` — بدون نیاز به احراز هویت.

### احراز هویت

```http
POST /api/v1/auth/login/
Content-Type: application/json

{"username": "demo_student", "password": "demo1234"}
```

توکن برگشتی را در درخواست‌های بعدی ارسال کنید:

```http
Authorization: Token <session_key>
```

| Endpoint | متد | توضیح |
|----------|-----|--------|
| `/api/v1/auth/login/` | POST | ورود |
| `/api/v1/auth/logout/` | POST | خروج |
| `/api/v1/auth/me/` | GET | پروفایل کاربر جاری |
| `/api/v1/auth/password/reset/` | POST | بازیابی رمز عبور |

### دامنه‌های API (نسخه v1)

تمام منابع CRUD زیر `/api/v1/` قرار دارند و از pagination (۲۰ مورد در صفحه)، جستجو، مرتب‌سازی و فیلتر پشتیبانی می‌کنند.

| Tag | منابع |
|-----|--------|
| **Authentication** | login، logout، me، password reset |
| **Auth Entities** | auth-roles، auth-accounts، auth-sessions، auth-account-roles |
| **Lookup** | const-values، departments، education-branches، tendencies، terms |
| **Person & Contact** | persons، phone-numbers، email-addresses، person-skills، postal-addresses |
| **Profiles** | teachers، students، employees، teacher-research-interests |
| **Academic** | lessons، classes، class-offers، exams، exam-results، attendances، transcripts و … |
| **Finance & Requests** | student-payments، student-requests، loans، scholarships، dormitory-requests و … |
| **Library & Misc** | books، library-book-lendings، internships، academic-events و … |
| **Composite Pages** | `/api/v1/pages/dashboard/`، `grades/`، `financial/` و … (یک درخواست برای هر صفحه) |

---

## معماری API

```
core/api/
├── authentication.py    # احراز هویت Token + Session
├── permissions.py       # دسترسی مبتنی بر نقش (student، admin و …)
├── pagination.py        # صفحه‌بندی استاندارد (۲۰ مورد)
├── mixins.py            # فیلتر queryset محدود به دانشجو
├── urls.py              # تمام مسیرهای v1
├── openapi/             # گروه tag، decoratorها، extension احراز هویت
├── serializers/         # ۷ ماژول serializer (۴۱ موجودیت)
├── views/               # ViewSetها + auth + APIهای ترکیبی صفحات
└── tests.py             # تست‌های smoke API
```

---

## پنل دانشجویی (Frontend)

صفحات HTML دانشجویی از طریق Django با slugهای انگلیسی سرو می‌شوند:

| مسیر | صفحه |
|------|------|
| `/` یا `/login/` | ورود |
| `/dashboard/` | داشبورد |
| `/logout/` | خروج (پاک‌سازی session و token) |
| `/teachers/`، `/financial/`، `/grades/` و … | سایر صفحات |

فونت **یکان بخ** در تمام صفحات از مسیر `/static/amoozeshyar/yekan-bakh.css` بارگذاری می‌شود.

---

## دستورات پرکاربرد

```bash
python manage.py runserver
python manage.py migrate
python manage.py seed_api_demo
python manage.py smoke_test_api --seed
python manage.py test core.api
python manage.py spectacular --file schema.yaml --validate
python manage.py createsuperuser
python manage.py check
```

---

## راهنماهای HTML

| URL | محتوا |
|-----|--------|
| `/docs/` | راهنمای اجرا و پنل ادمین |
| `/docs/setup-theme/` | راهنمای نصب و تم |
| `/docs/django-admin/` | راهنمای کامل Django Admin |
| [`docs/AUTH_GUIDE.md`](docs/AUTH_GUIDE.md) | راهنمای احراز هویت API (Postman، Token، مثال‌ها) |
