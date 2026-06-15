"""سریالایزرهای پروفایل اساتید، دانشجویان و کارمندان."""

from rest_framework import serializers

from core.models import Employee, Student, Teacher, TeacherResearchInterest


class TeacherSerializer(serializers.ModelSerializer):
    """پروفایل استاد."""

    person_name = serializers.CharField(source="person.full_name", read_only=True, allow_null=True)

    class Meta:
        model = Teacher
        fields = "__all__"


class TeacherResearchInterestSerializer(serializers.ModelSerializer):
    """علاقه پژوهشی استاد."""

    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = TeacherResearchInterest
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    """پروفایل دانشجو."""

    person_name = serializers.CharField(source="person.full_name", read_only=True, allow_null=True)
    department_title = serializers.CharField(source="department.department_title", read_only=True, allow_null=True)
    branch_title = serializers.CharField(source="branch.title", read_only=True, allow_null=True)
    tendency_name = serializers.CharField(source="tendency.tendency_name", read_only=True, allow_null=True)

    class Meta:
        model = Student
        fields = "__all__"


class StudentBriefSerializer(serializers.ModelSerializer):
    """نمای خلاصه دانشجو برای APIهای ترکیبی."""

    person_name = serializers.CharField(source="person.full_name", read_only=True, allow_null=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "student_number",
            "person",
            "person_name",
            "gpa",
            "current_term_gpa",
            "taken_units",
            "department",
            "branch",
            "tendency",
            "is_active",
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    """پروفایل کارمند."""

    person_name = serializers.CharField(source="person.full_name", read_only=True, allow_null=True)
    department_title = serializers.CharField(source="department.department_title", read_only=True, allow_null=True)

    class Meta:
        model = Employee
        fields = "__all__"
