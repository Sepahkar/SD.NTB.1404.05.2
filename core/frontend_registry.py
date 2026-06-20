"""Frontend page registry — English URL slugs mapped to HTML files."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

FRONTEND_ROOT = Path(__file__).resolve().parent.parent / "frontend"


@dataclass(frozen=True)
class FrontendPage:
    directory: str
    html_file: str
    requires_auth: bool = True
    render_mode: Literal["static", "api", "template"] = "api"
    template_name: str | None = None


FRONTEND_PAGES: dict[str, FrontendPage] = {
    "login": FrontendPage(
        directory="لاگین و فراموشی رمز عبور",
        html_file="azad_login.html",
        requires_auth=False,
        render_mode="api",
    ),
    "dashboard": FrontendPage(
        directory="داشبورد اصلی/main_dashbord-ElaheHashemabadi",
        html_file="index.html",
        render_mode="api",
    ),
    "teachers": FrontendPage(
        directory="معرفی اساتید/dashbord",
        html_file="index.html",
        render_mode="template",
        template_name="student/teachers.html",
    ),
    "course-selection": FrontendPage(
        directory="پنل انتخاب واحد",
        html_file="index.html",
        render_mode="api",
    ),
    "add-drop": FrontendPage(
        directory="حذف و اضافه/dashbord",
        html_file="index.html",
        render_mode="api",
    ),
    "add-drop-2": FrontendPage(
        directory="حذف و اضافه 2",
        html_file="DeleteandAdd.html",
        render_mode="static",
    ),
    "emergency-removal": FrontendPage(
        directory="حذف اضطراری",
        html_file="EmergencyRemoval.html",
        render_mode="api",
    ),
    "full-transcript": FrontendPage(
        directory="کارنامه کل/کارنامه کل-ElaheHashemabadi",
        html_file="index.html",
        render_mode="template",
        template_name="student/full_transcript.html",
    ),
    "semester-transcript": FrontendPage(
        directory="کارنامه نیمسال جاری",
        html_file="semester-report.html",
        render_mode="template",
        template_name="student/semester_transcript.html",
    ),
    "grades": FrontendPage(
        directory="کارنامه و نمرات",
        html_file="index.html",
        render_mode="template",
        template_name="student/grades.html",
    ),
    "financial": FrontendPage(
        directory="امور مالی/financial-dashboard",
        html_file="index.html",
        render_mode="template",
        template_name="student/financial.html",
    ),
    "debts": FrontendPage(
        directory="بدهی ها/Debt-dashboard",
        html_file="index.html",
        render_mode="template",
        template_name="student/debts.html",
    ),
    "payment-history": FrontendPage(
        directory="تاریخچه پرداختها",
        html_file="index.html",
        render_mode="template",
        template_name="student/payment_history.html",
    ),
    "loan-request": FrontendPage(
        directory="درخواست وام",
        html_file="index.html",
        render_mode="api",
    ),
    "student-requests": FrontendPage(
        directory="ارسال درخواست/dashbord",
        html_file="index.html",
        render_mode="api",
    ),
    "leave-request": FrontendPage(
        directory="درخواست مجوز/dashbord",
        html_file="index.html",
        render_mode="api",
    ),
    "grade-objection": FrontendPage(
        directory="اعتراض به نمره 1 و 2/اعتراض به نمره2",
        html_file="page1-grade-objection.html",
        render_mode="api",
    ),
    "grade-objection-form": FrontendPage(
        directory="اعتراض به نمره 1 و 2/اعتراض به نمره2",
        html_file="page2-objection-form.html",
        render_mode="api",
    ),
    "admin-financial": FrontendPage(
        directory="مدیریت امور مالی/financial-dashboard",
        html_file="index.html",
        render_mode="template",
        template_name="student/admin_financial.html",
    ),
    "sample-menu": FrontendPage(
        directory="منوی سمپل (اصلی )/dashbord",
        html_file="index.html",
        render_mode="static",
    ),
}

# Persian sidebar label → URL slug
NAV_LINKS: dict[str, str] = {
    "داشبورد": "dashboard",
    "معرفی اساتید": "teachers",
    "انتخاب واحد": "course-selection",
    "حذف و اضافه": "add-drop",
    "جستجوی دروس": "course-selection",
    "حذف اضطراری": "emergency-removal",
    "کارنامه کل": "full-transcript",
    "کارنامه کلی": "full-transcript",
    "کارنامه نیمسال": "semester-transcript",
    "کارنامه و نمرات": "grades",
    "اعتراض به نمره": "grade-objection",
    "امور مالی": "financial",
    "بدهی‌ها": "debts",
    "بدهی ها": "debts",
    "تاریخچه پرداخت": "payment-history",
    "تاریخچه پرداختها": "payment-history",
    "درخواست وام": "loan-request",
    "ارسال درخواست": "student-requests",
    "درخواست مجوز": "leave-request",
}

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".zip": "application/zip",
}


def get_page_directory(slug: str) -> Path | None:
    page = FRONTEND_PAGES.get(slug)
    if not page:
        return None
    return FRONTEND_ROOT / page.directory


def get_page_html_path(slug: str) -> Path | None:
    page = FRONTEND_PAGES.get(slug)
    if not page:
        return None
    path = FRONTEND_ROOT / page.directory / page.html_file
    return path if path.is_file() else None
