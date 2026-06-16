from rest_framework import viewsets

from core.api.mixins import BorrowerScopedQuerysetMixin, StudentScopedQuerysetMixin
from core.api.openapi.decorators import tagged_viewset
from core.api.openapi.tags import TAG_FINANCE
from core.api.permissions import AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff
from core.api.serializers.finance import (
    AcademicLeaveRequestSerializer,
    DormitoryRequestSerializer,
    LoanSerializer,
    ScholarshipSerializer,
    StudentPaymentsSerializer,
    StudentRequestSerializer,
)
from core.models import (
    AcademicLeaveRequest,
    DormitoryRequest,
    Loan,
    Scholarship,
    StudentPayments,
    StudentRequest,
)


@tagged_viewset(TAG_FINANCE, "پرداخت‌های دانشجو")
class StudentPaymentsViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = StudentPayments.objects.select_related("student").all()
    serializer_class = StudentPaymentsSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "is_confirmed"]


@tagged_viewset(TAG_FINANCE, "درخواست‌های دانشجو")
class StudentRequestViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = StudentRequest.objects.select_related(
        "student", "request_type", "status", "employee_follower"
    ).all()
    serializer_class = StudentRequestSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "request_type", "status"]


@tagged_viewset(TAG_FINANCE, "درخواست مرخصی تحصیلی")
class AcademicLeaveRequestViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = AcademicLeaveRequest.objects.select_related("student").all()
    serializer_class = AcademicLeaveRequestSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "is_approved"]


@tagged_viewset(TAG_FINANCE, "بورسیه‌ها")
class ScholarshipViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Scholarship.objects.select_related("student").all()
    serializer_class = ScholarshipSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "status"]


@tagged_viewset(TAG_FINANCE, "درخواست خوابگاه")
class DormitoryRequestViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = DormitoryRequest.objects.select_related("student").all()
    serializer_class = DormitoryRequestSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "approval_status"]


@tagged_viewset(TAG_FINANCE, "وام‌ها")
class LoanViewSet(BorrowerScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Loan.objects.select_related("borrower").all()
    serializer_class = LoanSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["borrower", "loan_status", "loan_type"]
    search_fields = ["loan_file_number"]
