"""Unit tests for Django template-based student pages."""

from django.test import Client, TestCase

from core.unit_tests.base import seed


class StudentTemplateViewsUnitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed()

    def _logged_in_client(self):
        client = Client()
        response = client.post(
            "/api/v1/auth/login/",
            data='{"username":"demo_student","password":"demo1234"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return client

    def test_template_pages_redirect_anonymous(self):
        client = Client()
        for path in ["/teachers/", "/financial/", "/grades/", "/full-transcript/"]:
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.status_code, 302)

    def test_template_pages_with_session(self):
        client = self._logged_in_client()
        for path in ["/teachers/", "/financial/", "/grades/", "/payment-history/"]:
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.status_code, 200, path)

    def test_add_drop_2_redirects(self):
        response = Client().get("/add-drop-2/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("add-drop", response.url)
