from django.test import TestCase
from django.urls import reverse

class APIDocumentationTests(TestCase):
    def test_ping_endpoint(self):
        """
        Verify that the ping healthcheck endpoint is online and returns JSON.
        """
        response = self.client.get(reverse('ping'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "API is online"})

    def test_openapi_schema_endpoint(self):
        """
        Verify that the OpenAPI JSON schema endpoint is accessible.
        """
        response = self.client.get(reverse('schema'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.oai.openapi', response['Content-Type'])

    def test_swagger_ui_endpoint(self):
        """
        Verify that the Swagger UI documentation page loads correctly.
        """
        response = self.client.get(reverse('swagger-ui'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'swagger-ui')

    def test_redoc_endpoint(self):
        """
        Verify that the ReDoc documentation page loads correctly.
        """
        response = self.client.get(reverse('redoc'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'redoc')
