"""Shared serializers for OpenAPI response schemas."""

from rest_framework import serializers


class DetailResponseSerializer(serializers.Serializer):
    """پاسخ ساده با پیام detail."""

    detail = serializers.CharField(help_text="پیام توضیحی")
