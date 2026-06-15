"""سریالایزرهای مالی و درخواست‌های دانشجویی."""

from rest_framework import serializers

from core.models import (
    AcademicLeaveRequest,
    DormitoryRequest,
    Loan,
    Scholarship,
    StudentPayments,
    StudentRequest,
)


class StudentPaymentsSerializer(serializers.ModelSerializer):
    """پرداخت دانشجو."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)

    class Meta:
        model = StudentPayments
        fields = "__all__"


class StudentRequestSerializer(serializers.ModelSerializer):
    """درخواست عمومی دانشجو."""

    student_number = serializers.CharField(source="student.student_number", read_only=True, allow_null=True)
    request_type_caption = serializers.CharField(source="request_type.caption", read_only=True)
    status_caption = serializers.CharField(source="status.caption", read_only=True)

    class Meta:
        model = StudentRequest
        fields = "__all__"


class AcademicLeaveRequestSerializer(serializers.ModelSerializer):
    """درخواست مرخصی تحصیلی."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)

    class Meta:
        model = AcademicLeaveRequest
        fields = "__all__"


class ScholarshipSerializer(serializers.ModelSerializer):
    """بورسیه دانشجو."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)

    class Meta:
        model = Scholarship
        fields = "__all__"


class DormitoryRequestSerializer(serializers.ModelSerializer):
    """درخواست خوابگاه."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)

    class Meta:
        model = DormitoryRequest
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    """وام."""

    borrower_name = serializers.CharField(source="borrower.full_name", read_only=True)

    class Meta:
        model = Loan
        fields = "__all__"
