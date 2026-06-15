from rest_framework import viewsets

from core.api.openapi.decorators import tagged_viewset
from core.api.openapi.tags import TAG_PROFILES
from core.api.permissions import AdminWriteAuthenticatedRead
from core.api.serializers.profiles import (
    EmployeeSerializer,
    StudentSerializer,
    TeacherResearchInterestSerializer,
    TeacherSerializer,
)
from core.models import Employee, Student, Teacher, TeacherResearchInterest


@tagged_viewset(TAG_PROFILES, "اساتید")
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related("person").all()
    serializer_class = TeacherSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    search_fields = ["full_name", "person__full_name"]


@tagged_viewset(TAG_PROFILES, "علایق پژوهشی اساتید")
class TeacherResearchInterestViewSet(viewsets.ModelViewSet):
    queryset = TeacherResearchInterest.objects.select_related("teacher").all()
    serializer_class = TeacherResearchInterestSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["teacher"]


@tagged_viewset(TAG_PROFILES, "دانشجویان")
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related(
        "person", "department", "branch", "tendency", "advisor_teacher"
    ).all()
    serializer_class = StudentSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["department", "branch", "tendency", "is_active", "graduation_status"]
    search_fields = ["student_number", "person__full_name", "first_name", "last_name"]


@tagged_viewset(TAG_PROFILES, "کارمندان")
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("person", "department", "position").all()
    serializer_class = EmployeeSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["department", "is_active"]
    search_fields = ["employee_code", "personnel_code", "person__full_name"]
