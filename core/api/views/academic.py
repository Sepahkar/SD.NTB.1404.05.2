from rest_framework import viewsets

from core.api.mixins import StudentScopedQuerysetMixin
from core.api.openapi.decorators import tagged_viewset
from core.api.openapi.tags import TAG_ACADEMIC
from core.api.permissions import AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff
from core.api.serializers.academic import (
    AttendanceSerializer,
    ClassOfferSerializer,
    ClassSerializer,
    ExamInvigilatorSerializer,
    ExamResultSerializer,
    ExamSerializer,
    LessonSerializer,
    PrerequisiteWarningSerializer,
    TeacherEvaluationSerializer,
    TranscriptSerializer,
)
from core.models import (
    Attendance,
    Class,
    ClassOffer,
    Exam,
    ExamInvigilator,
    ExamResult,
    Lesson,
    PrerequisiteWarning,
    TeacherEvaluation,
    Transcript,
)


@tagged_viewset(TAG_ACADEMIC, "دروس")
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related("department", "education_branch").prefetch_related("prerequisites").all()
    serializer_class = LessonSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["department", "education_branch", "is_active"]
    search_fields = ["lesson_code", "title"]


@tagged_viewset(TAG_ACADEMIC, "گروه‌های درسی")
class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.select_related("term", "lesson", "tendency").all()
    serializer_class = ClassSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["term", "lesson", "tendency"]
    search_fields = ["class_number"]


@tagged_viewset(TAG_ACADEMIC, "ارائه کلاس‌ها")
class ClassOfferViewSet(viewsets.ModelViewSet):
    queryset = ClassOffer.objects.select_related("class_group", "teacher", "term").all()
    serializer_class = ClassOfferSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["term", "teacher", "class_group"]


@tagged_viewset(TAG_ACADEMIC, "امتحانات")
class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related("class_offer").all()
    serializer_class = ExamSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["class_offer", "exam_type"]


@tagged_viewset(TAG_ACADEMIC, "مراقبین امتحان")
class ExamInvigilatorViewSet(viewsets.ModelViewSet):
    queryset = ExamInvigilator.objects.select_related("exam", "employee").all()
    serializer_class = ExamInvigilatorSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["exam", "employee"]


@tagged_viewset(TAG_ACADEMIC, "نتایج امتحان")
class ExamResultViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = ExamResult.objects.select_related("student", "exam").all()
    serializer_class = ExamResultSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "exam", "status"]


@tagged_viewset(TAG_ACADEMIC, "حضور و غیاب")
class AttendanceViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related("student", "class_offer").all()
    serializer_class = AttendanceSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "class_offer", "attendance_status"]


@tagged_viewset(TAG_ACADEMIC, "کارنامه")
class TranscriptViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Transcript.objects.select_related(
        "student", "class_offer", "class_offer__class_group", "class_offer__class_group__lesson", "class_offer__term"
    ).all()
    serializer_class = TranscriptSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "class_offer", "pass_status"]


@tagged_viewset(TAG_ACADEMIC, "ارزیابی استاد")
class TeacherEvaluationViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = TeacherEvaluation.objects.select_related("teacher", "student", "term").all()
    serializer_class = TeacherEvaluationSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["teacher", "student", "term"]


@tagged_viewset(TAG_ACADEMIC, "هشدار پیش‌نیاز")
class PrerequisiteWarningViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = PrerequisiteWarning.objects.select_related("student", "lesson", "term").all()
    serializer_class = PrerequisiteWarningSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "lesson", "term", "is_active"]
