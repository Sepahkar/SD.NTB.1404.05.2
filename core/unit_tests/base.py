"""Shared helpers for API unit tests."""

from io import StringIO

from rest_framework.test import APIClient

from core.seed.demo_data import seed_demo_data


def seed():
    seed_demo_data(stdout=StringIO())


def login_client(username="demo_student", password="demo1234"):
    client = APIClient()
    response = client.post(
        "/api/v1/auth/login/",
        {"username": username, "password": password},
        format="json",
    )
    assert response.status_code == 200, response.data
    client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
    return client, response.data["token"]


AUTH_ENDPOINTS = [
    ("POST", "/api/v1/auth/login/"),
    ("POST", "/api/v1/auth/logout/"),
    ("GET", "/api/v1/auth/me/"),
    ("POST", "/api/v1/auth/password/reset/"),
]

COMPOSITE_GET_ENDPOINTS = [
    "/api/v1/pages/dashboard/",
    "/api/v1/pages/semester-transcript/",
    "/api/v1/pages/full-transcript/",
    "/api/v1/pages/grades/",
    "/api/v1/pages/course-selection/",
    "/api/v1/pages/add-drop/",
    "/api/v1/pages/financial/",
    "/api/v1/pages/payment-history/",
    "/api/v1/pages/loan-request/",
    "/api/v1/pages/student-requests/",
    "/api/v1/pages/leave-request/",
    "/api/v1/pages/teachers/",
    "/api/v1/pages/grade-objection/",
]

CRUD_LIST_ENDPOINTS = [
    "const-values",
    "departments",
    "education-branches",
    "tendencies",
    "terms",
    "persons",
    "phone-numbers",
    "email-addresses",
    "person-skills",
    "postal-addresses",
    "teachers",
    "teacher-research-interests",
    "students",
    "employees",
    "lessons",
    "classes",
    "class-offers",
    "exams",
    "exam-invigilators",
    "exam-results",
    "attendances",
    "transcripts",
    "teacher-evaluations",
    "prerequisite-warnings",
    "student-payments",
    "student-requests",
    "academic-leave-requests",
    "scholarships",
    "dormitory-requests",
    "loans",
    "books",
    "library-book-lendings",
    "library-reserves",
    "companies",
    "internships",
    "document-students",
    "academic-programs",
    "academic-events",
    "academic-announcements",
    "auth-roles",
    "auth-accounts",
    "auth-sessions",
    "auth-account-roles",
]

STUDENT_DENIED_ENDPOINTS = [
    "persons",
    "auth-roles",
    "auth-accounts",
    "auth-sessions",
    "auth-account-roles",
]
