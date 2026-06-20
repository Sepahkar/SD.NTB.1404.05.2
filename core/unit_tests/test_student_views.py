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

    def test_template_pages_served_as_static_html(self):
        client = Client()
        for path in ["/teachers/", "/financial/", "/grades/", "/full-transcript/"]:
            with self.subTest(path=path):
                response = client.get(path)
                self.assertEqual(response.status_code, 200, path)

    def test_admin_financial_redirects_anonymous(self):
        response = Client().get("/admin-financial/")
        self.assertEqual(response.status_code, 302)

    def test_add_drop_2_redirects(self):
        response = Client().get("/add-drop-2/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("add-drop", response.url)

    def test_add_drop_page_served(self):
        response = Client().get("/add-drop/")
        self.assertEqual(response.status_code, 200)

    def test_emergency_removal_page_served(self):
        response = Client().get("/emergency-removal/")
        self.assertEqual(response.status_code, 200)

    def test_course_search_page_served(self):
        response = Client().get("/course-search/")
        self.assertEqual(response.status_code, 200)

    def test_served_html_includes_notification_shell(self):
        response = Client().get("/teachers/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("student-panel", content)
        self.assertIn("notifications.js", content)
