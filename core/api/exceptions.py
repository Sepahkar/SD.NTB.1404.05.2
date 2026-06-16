from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Ensure authentication failures always return HTTP 401."""
    response = exception_handler(exc, context)
    if response is not None and isinstance(exc, AuthenticationFailed):
        response.status_code = 401
    return response
