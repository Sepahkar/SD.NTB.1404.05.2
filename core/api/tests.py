"""API tests for Amoozeshyar."""
from io import StringIO

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import AuthAccount, AuthRole, Department, Person, Student, Term
from core.seed.demo_data import seed_demo_data


class APISmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role, _ = AuthRole.objects.get_or_create(code="student", defaults={"name": "دانشجو"})
        admin_role, _ = AuthRole.objects.get_or_create(code="admin", defaults={"name": "مدیر"})

        self.person = Person.objects.create(
            username="test_student",
            password=make_password("test1234"),
            national_code="1234567890",
            first_name="تست",
            last_name="دانشجو",
        )
        self.account = AuthAccount.objects.create(
            person=self.person,
            username="test_student",
            email="test@example.com",
            password_hash=make_password("test1234"),
        )
        self.account.roles.add(self.role)

        dept = Department.objects.create(
            department_code="CS",
            department_title="مهندسی کامپیوتر",
        )
        Student.objects.create(
            person=self.person,
            student_number="99123456",
            department=dept,
        )
        Term.objects.create(
            term_id=14031,
            term_title="نیمسال اول 1403",
            start_term="2024-09-23",
            end_term="2025-02-19",
            is_current=True,
            registration_start=timezone.now(),
        )

    def test_ping_public(self):
        response = self.client.get("/api/ping/")
        self.assertEqual(response.status_code, 200)

    def test_login_and_me(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "test_student", "password": "test1234"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        token = response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        me = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["account"]["username"], "test_student")

    def test_dashboard_page(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "test_student", "password": "test1234"},
            format="json",
        )
        token = login.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.get("/api/v1/pages/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("student", response.data)

    def test_const_values_list_requires_auth(self):
        response = self.client.get("/api/v1/const-values/")
        self.assertEqual(response.status_code, 401)

    def test_me_rejects_invalid_authorization_header_with_session_cookie(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "test_student", "password": "test1234"},
            format="json",
        )
        self.assertEqual(login.status_code, 200)

        self.client.credentials(HTTP_AUTHORIZATION="fake_key")
        me = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me.status_code, 401)
        self.assertIn("detail", me.data)
        self.assertIn("Token", me.data["detail"])

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token'][:-1]}x")
        me = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me.status_code, 401)
        self.assertIn("detail", me.data)

    def test_me_accepts_token_without_session_cookie(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "test_student", "password": "test1234"},
            format="json",
        )
        token = login.data["token"]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        me = client.get("/api/v1/auth/me/")
        self.assertEqual(me.status_code, 200)


COMPOSITE_PAGES = [
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

STUDENT_SCOPED_ENDPOINTS = [
    "/api/v1/student-payments/",
    "/api/v1/transcripts/",
    "/api/v1/exam-results/",
    "/api/v1/student-requests/",
]


class DemoSeedIntegrationTests(TestCase):
    """Integration tests using full demo seed data."""

    @classmethod
    def setUpTestData(cls):
        seed_demo_data(stdout=StringIO())

    def _login(self, username="demo_student", password="demo1234"):
        client = APIClient()
        response = client.post(
            "/api/v1/auth/login/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        return client

    def test_all_composite_pages_return_200_for_student(self):
        client = self._login()
        for url in COMPOSITE_PAGES:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 200, response.data)

    def test_dashboard_has_seeded_content(self):
        client = self._login()
        response = client.get("/api/v1/pages/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data.get("student"))
        self.assertIsNotNone(response.data.get("current_term"))
        self.assertGreaterEqual(len(response.data.get("announcements", [])), 1)

    def test_student_denied_admin_endpoints(self):
        client = self._login("demo_student")
        for url in ["/api/v1/persons/", "/api/v1/auth-accounts/", "/api/v1/auth-roles/"]:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_admin_can_access_auth_entities(self):
        client = self._login("demo_admin")
        response = client.get("/api/v1/auth-accounts/")
        self.assertEqual(response.status_code, 200)
        response = client.get("/api/v1/persons/")
        self.assertEqual(response.status_code, 200)

    def test_student_scoped_endpoints_return_own_records(self):
        client = self._login("demo_student")
        for url in STUDENT_SCOPED_ENDPOINTS:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)
                results = response.data.get("results", response.data)
                self.assertGreaterEqual(len(results), 1)

    def test_financial_page_has_payments(self):
        client = self._login()
        response = client.get("/api/v1/pages/financial/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data.get("payments", [])), 1)
        self.assertGreater(response.data.get("total_paid", 0), 0)

    def test_admin_gets_404_on_student_only_composite_pages(self):
        client = self._login("demo_admin")
        student_only_pages = [
            "/api/v1/pages/dashboard/",
            "/api/v1/pages/financial/",
            "/api/v1/pages/course-selection/",
            "/api/v1/pages/grade-objection/",
        ]
        for url in student_only_pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 404, response.data)
                self.assertIn("پروفایل دانشجو", response.data["detail"])

    def test_grade_objection_page_has_seeded_objections(self):
        client = self._login()
        response = client.get("/api/v1/pages/grade-objection/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data.get("objections", [])), 1)

    def test_student_phone_numbers_scoped_to_self(self):
        client = self._login("demo_student")
        response = client.get("/api/v1/phone-numbers/")
        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", [])
        self.assertGreaterEqual(len(results), 1)
        for row in results:
            self.assertEqual(row["person"], client.get("/api/v1/auth/me/").data["person"]["id"])

    def test_student_loans_scoped_to_self(self):
        client = self._login("demo_student")
        response = client.get("/api/v1/loans/")
        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", [])
        self.assertGreaterEqual(len(results), 1)


STUDENT_ONLY_COMPOSITE_PAGES = [
    "/api/v1/pages/dashboard/",
    "/api/v1/pages/semester-transcript/",
    "/api/v1/pages/full-transcript/",
    "/api/v1/pages/grades/",
    "/api/v1/pages/course-selection/",
    "/api/v1/pages/add-drop/",
    "/api/v1/pages/financial/",
    "/api/v1/pages/payment-history/",
    "/api/v1/pages/student-requests/",
    "/api/v1/pages/leave-request/",
    "/api/v1/pages/grade-objection/",
]


class HTTPErrorLogicTests(TestCase):
    """Verify HTTP 400+ status codes and error message semantics."""

    @classmethod
    def setUpTestData(cls):
        seed_demo_data(stdout=StringIO())

    def _login(self, username="demo_student", password="demo1234"):
        client = APIClient()
        response = client.post(
            "/api/v1/auth/login/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        return client

    def test_me_without_auth_returns_401(self):
        response = APIClient().get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_me_with_bad_authorization_format_returns_401(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="fake_key")
        response = client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Token", response.data["detail"])

    def test_me_with_invalid_token_returns_401(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token invalidtoken000")
        response = client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 401)
        self.assertIn("توکن", response.data["detail"])

    def test_login_wrong_password_returns_401(self):
        response = APIClient().post(
            "/api/v1/auth/login/",
            {"username": "demo_student", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_login_missing_field_returns_400(self):
        response = APIClient().post(
            "/api/v1/auth/login/",
            {"username": "demo_student"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_password_reset_wrong_answer_returns_400(self):
        response = APIClient().post(
            "/api/v1/auth/password/reset/",
            {
                "username": "demo_student",
                "security_answer": "wrong",
                "new_password": "newpass1234",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_password_reset_unknown_user_returns_404(self):
        response = APIClient().post(
            "/api/v1/auth/password/reset/",
            {
                "username": "nobody_here",
                "security_answer": "tehran",
                "new_password": "newpass1234",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_student_denied_persons_returns_403(self):
        client = self._login()
        response = client.get("/api/v1/persons/")
        self.assertEqual(response.status_code, 403)

    def test_student_denied_department_write_returns_403(self):
        client = self._login()
        response = client.post(
            "/api/v1/departments/",
            {"department_code": "X", "department_title": "Test"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_missing_student_record_returns_404(self):
        client = self._login()
        response = client.get("/api/v1/students/999999/")
        self.assertEqual(response.status_code, 404)

    def test_admin_financial_page_returns_404(self):
        client = self._login("demo_admin")
        response = client.get("/api/v1/pages/financial/")
        self.assertEqual(response.status_code, 404)

    def test_student_financial_page_returns_200(self):
        client = self._login()
        response = client.get("/api/v1/pages/financial/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data.get("payments", [])), 1)
