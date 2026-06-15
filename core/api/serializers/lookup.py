"""سریالایزرهای داده‌های مرجع (Lookup)."""

from rest_framework import serializers

from core.models import (
    ConstValue,
    Department,
    EducationBranch,
    Tendency,
    Term,
)


class ConstValueSerializer(serializers.ModelSerializer):
    """مقدار ثابت سیستم (نوع درخواست، وضعیت و ...)."""

    class Meta:
        model = ConstValue
        fields = "__all__"


class ConstValueBriefSerializer(serializers.ModelSerializer):
    """نمای خلاصه مقدار ثابت."""

    class Meta:
        model = ConstValue
        fields = ["id", "caption", "code", "name", "value", "value_title"]


class DepartmentSerializer(serializers.ModelSerializer):
    """دانشکده / دپارتمان."""

    class Meta:
        model = Department
        fields = "__all__"


class EducationBranchSerializer(serializers.ModelSerializer):
    """گرایش آموزشی (رشته)."""

    department_title = serializers.CharField(
        source="department.department_title", read_only=True, help_text="عنوان دانشکده"
    )

    class Meta:
        model = EducationBranch
        fields = "__all__"


class TendencySerializer(serializers.ModelSerializer):
    """گرایش تخصصی."""

    field_title = serializers.CharField(source="field.title", read_only=True, allow_null=True, help_text="عنوان رشته")

    class Meta:
        model = Tendency
        fields = "__all__"


class TermSerializer(serializers.ModelSerializer):
    """نیمسال تحصیلی."""

    class Meta:
        model = Term
        fields = "__all__"
