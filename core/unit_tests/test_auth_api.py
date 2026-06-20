"""Unit tests for authentication API endpoints."""

from django.test import TestCase
from rest_framework.test import APIClient

from core.unit_tests.base import AUTH_ENDPOINTS, login_client, seed


class AuthAPIUnitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed()

    def test_ping_public(self):
        response = APIClient().get("/api/ping/")
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        client = APIClient()
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "demo_student", "password": "demo1234"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_login_wrong_password(self):
        response = APIClient().post(
            "/api/v1/auth/login/",
            {"username": "demo_student", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_me_requires_auth(self):
        response = APIClient().get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_me_with_token(self):
        client, _ = login_client()
        response = client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["account"]["username"], "demo_student")

    def test_logout(self):
        client, _ = login_client()
        response = client.post("/api/v1/auth/logout/")
        self.assertIn(response.status_code, (200, 204))

    def test_password_reset_wrong_answer(self):
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

    def test_all_auth_endpoints_exist(self):
        client, _ = login_client()
        for method, url in AUTH_ENDPOINTS:
            if url.endswith("login/") or url.endswith("password/reset/"):
                continue
            if method == "GET":
                response = client.get(url)
            else:
                response = client.post(url, {}, format="json")
            self.assertNotEqual(response.status_code, 404, url)
