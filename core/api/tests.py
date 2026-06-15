"""API tests for Amoozeshyar."""
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import AuthAccount, AuthRole, Department, Person, Student, Term


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
        self.assertEqual(response.status_code, 403)
