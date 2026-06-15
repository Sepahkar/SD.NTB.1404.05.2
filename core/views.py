from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.api.openapi.tags import TAG_HEALTH

class PingResponseSerializer(serializers.Serializer):
    """پاسخ بررسی سلامت سرویس."""
    status = serializers.CharField(help_text="وضعیت سرویس (ok در حالت عادی)")
    message = serializers.CharField(help_text="پیام توضیحی وضعیت")


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_HEALTH],
        summary="بررسی سلامت سرویس",
        description=(
            "بررسی در دسترس بودن API. بدون نیاز به احراز هویت.\n\n"
            "در صورت سالم بودن سرویس، status=ok برگردانده می‌شود."
        ),
        responses={200: PingResponseSerializer},
    ),
)
class PingAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = PingResponseSerializer(data={"status": "ok", "message": "API is online"})
        serializer.is_valid()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
