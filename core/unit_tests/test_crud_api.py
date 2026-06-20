"""Unit tests for CRUD router API endpoints."""

from django.test import TestCase
from rest_framework.test import APIClient

from core.unit_tests.base import CRUD_LIST_ENDPOINTS, STUDENT_DENIED_ENDPOINTS, login_client, seed


class CRUDAPIUnitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed()

    def test_student_list_all_crud_endpoints(self):
        client, _ = login_client()
        for ep in CRUD_LIST_ENDPOINTS:
            url = f"/api/v1/{ep}/"
            with self.subTest(endpoint=ep):
                response = client.get(url)
                if ep in STUDENT_DENIED_ENDPOINTS:
                    self.assertEqual(response.status_code, 403, url)
                else:
                    self.assertEqual(response.status_code, 200, url)

    def test_admin_can_access_auth_entities(self):
        client, _ = login_client("demo_admin")
        for ep in ["auth-accounts", "persons", "auth-roles"]:
            response = client.get(f"/api/v1/{ep}/")
            self.assertEqual(response.status_code, 200, ep)

    def test_student_cannot_write_departments(self):
        client, _ = login_client()
        response = client.post(
            "/api/v1/departments/",
            {"department_code": "X", "department_title": "Test"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_const_values_filter_by_code(self):
        client, _ = login_client()
        response = client.get("/api/v1/const-values/?code=grade_objection")
        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", response.data)
        self.assertGreaterEqual(len(results), 1)
