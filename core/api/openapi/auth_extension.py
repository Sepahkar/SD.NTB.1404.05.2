"""OpenAPI extensions for custom authentication."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class AuthSessionTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "core.api.authentication.AuthSessionTokenAuthentication"
    name = "TokenAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "فرمت: Token <session_key> — توکن دریافتی از POST /api/v1/auth/login/",
        }


class AuthSessionAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "core.api.authentication.AuthSessionAuthentication"
    name = "SessionAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "sessionid",
            "description": "نشست Django — پس از login با کوکی sessionid نیز قابل استفاده است.",
        }
