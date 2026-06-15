from rest_framework import viewsets

from core.api.openapi.decorators import tagged_viewset
from core.api.openapi.tags import TAG_LOOKUP
from core.api.permissions import AdminWriteAuthenticatedRead, ReadOnlyOrAdmin
from core.api.serializers.lookup import (
    ConstValueSerializer,
    DepartmentSerializer,
    EducationBranchSerializer,
    TendencySerializer,
    TermSerializer,
)
from core.models import ConstValue, Department, EducationBranch, Tendency, Term


@tagged_viewset(TAG_LOOKUP, "مقادیر ثابت")
class ConstValueViewSet(viewsets.ModelViewSet):
    queryset = ConstValue.objects.select_related("parent").all()
    serializer_class = ConstValueSerializer
    permission_classes = [ReadOnlyOrAdmin]
    filterset_fields = ["code", "is_active", "parent"]
    search_fields = ["caption", "code", "name", "value"]


@tagged_viewset(TAG_LOOKUP, "دانشکده‌ها")
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    search_fields = ["department_title", "department_code", "name"]


@tagged_viewset(TAG_LOOKUP, "گرایش‌های آموزشی")
class EducationBranchViewSet(viewsets.ModelViewSet):
    queryset = EducationBranch.objects.select_related("department").all()
    serializer_class = EducationBranchSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["department", "degree_level"]
    search_fields = ["title"]


@tagged_viewset(TAG_LOOKUP, "گرایش‌ها")
class TendencyViewSet(viewsets.ModelViewSet):
    queryset = Tendency.objects.select_related("field").all()
    serializer_class = TendencySerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["field", "is_active"]
    search_fields = ["tendency_name"]


@tagged_viewset(TAG_LOOKUP, "نیمسال‌های تحصیلی")
class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["is_current"]
    search_fields = ["term_title", "name"]
