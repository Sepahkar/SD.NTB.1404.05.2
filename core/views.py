from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema

class PingResponseSerializer(serializers.Serializer):
    status = serializers.CharField(help_text="Status of the API service.")
    message = serializers.CharField(help_text="Detailed status message.")

class PingAPIView(APIView):
    """
    A simple API view to check the API health status.
    """
    @extend_schema(
        summary="Health Check",
        description="Returns the status of the API service to check if it is running.",
        responses={200: PingResponseSerializer}
    )
    def get(self, request):
        serializer = PingResponseSerializer(data={"status": "ok", "message": "API is online"})
        serializer.is_valid()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
