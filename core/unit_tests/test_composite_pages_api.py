"""Unit tests for composite page API endpoints."""

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import ClassOffer, Transcript
from core.unit_tests.base import COMPOSITE_GET_ENDPOINTS, login_client, seed


class CompositePagesAPIUnitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed()

    def test_all_composite_get_endpoints_for_student(self):
        client, _ = login_client()
        for url in COMPOSITE_GET_ENDPOINTS:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 200, response.data)

    def test_dashboard_structure(self):
        client, _ = login_client()
        response = client.get("/api/v1/pages/dashboard/")
        self.assertIn("student", response.data)
        self.assertIn("announcements", response.data)
        self.assertIn("enrolled_courses", response.data)

    def test_course_selection_enroll_and_drop(self):
        client, _ = login_client()
        sel = client.get("/api/v1/pages/course-selection/")
        self.assertEqual(sel.status_code, 200)
        offers = sel.data.get("available_offers", [])
        if not offers:
            self.skipTest("No offers in seed data")
        offer_id = offers[0]["id"]
        before = Transcript.objects.filter(class_offer_id=offer_id).count()
        enroll = client.post(
            "/api/v1/pages/course-selection/",
            {"class_offer_id": offer_id},
            format="json",
        )
        if before == 0:
            self.assertEqual(enroll.status_code, 201, enroll.data)
            transcript_id = enroll.data["id"]
            drop = client.post(
                "/api/v1/pages/add-drop/",
                {"transcript_id": transcript_id},
                format="json",
            )
            self.assertEqual(drop.status_code, 200, drop.data)
        else:
            self.assertIn(enroll.status_code, (201, 400))

    def test_admin_denied_student_only_pages(self):
        client, _ = login_client("demo_admin")
        for url in [
            "/api/v1/pages/dashboard/",
            "/api/v1/pages/financial/",
        ]:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 404)

    def test_teachers_page_public_to_auth_users(self):
        client, _ = login_client()
        response = client.get("/api/v1/pages/teachers/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("teachers", response.data)
