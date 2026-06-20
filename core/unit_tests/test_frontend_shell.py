"""Unit tests for frontend HTML shell injection."""

from django.test import SimpleTestCase

from core.frontend_shell import enrich_frontend_html


class FrontendShellUnitTests(SimpleTestCase):
    def test_injects_shared_assets_for_authenticated_pages(self):
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div class="main-content"><div class="notification-icon"></div></div></body></html>"""
        enriched = enrich_frontend_html(html, "dashboard")
        self.assertIn('class="student-panel"', enriched)
        self.assertIn("/static/amoozeshyar/student-panel.css", enriched)
        self.assertIn("/static/amoozeshyar/notifications.js", enriched)
        self.assertIn("/static/amoozeshyar/api-client.js", enriched)

    def test_preserves_existing_body_class(self):
        html = '<html><head></head><body class="bg-light"><main></main></body></html>'
        enriched = enrich_frontend_html(html, "teachers")
        self.assertIn('class="bg-light student-panel"', enriched)

    def test_does_not_duplicate_existing_assets(self):
        html = """<html><head>
<link rel="stylesheet" href="/static/amoozeshyar/student-panel.css">
</head><body class="student-panel">
<script src="/static/amoozeshyar/api-client.js"></script>
<script src="/static/amoozeshyar/utils.js"></script>
<script src="/static/amoozeshyar/nav.js"></script>
<script src="/static/amoozeshyar/notifications.js"></script>
<script src="/static/amoozeshyar/auth.js"></script>
</body></html>"""
        enriched = enrich_frontend_html(html, "financial")
        self.assertEqual(enriched.count("student-panel.css"), 1)
        self.assertEqual(enriched.count("notifications.js"), 1)

    def test_login_page_is_not_enriched(self):
        html = "<html><head></head><body><main></main></body></html>"
        enriched = enrich_frontend_html(html, "login")
        self.assertNotIn("notifications.js", enriched)
        self.assertNotIn("student-panel", enriched)

    def test_script_order_is_preserved(self):
        html = """<html><head></head><body>
<script src="/static/amoozeshyar/auth.js"></script>
<script src="/static/amoozeshyar/pages/forms.js"></script>
</body></html>"""
        enriched = enrich_frontend_html(html, "course-selection")
        self.assertLess(enriched.index("api-client.js"), enriched.index("auth.js"))
        self.assertLess(enriched.index("notifications.js"), enriched.index("auth.js"))

    def test_unknown_slug_returns_original_html(self):
        html = "<html><body></body></html>"
        self.assertEqual(enrich_frontend_html(html, "missing"), html)
