from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "هسته آموزشیار"

    def ready(self):
        import core.api.openapi.auth_extension  # noqa: F401 — register OpenAPI auth scheme
