"""OpenAPI response serializers for composite page API views."""

from rest_framework import serializers

from core.api.serializers.academic import (
    ClassOfferSerializer,
    ExamResultSerializer,
    TranscriptSerializer,
)
from core.api.serializers.finance import (
    AcademicLeaveRequestSerializer,
    LoanSerializer,
    StudentPaymentsSerializer,
    StudentRequestSerializer,
)
from core.api.serializers.library_misc import AcademicAnnouncementSerializer
from core.api.serializers.profiles import StudentBriefSerializer, TeacherSerializer
from core.api.serializers.lookup import TermSerializer


class DebtSummarySerializer(serializers.Serializer):
    total_paid = serializers.DecimalField(max_digits=20, decimal_places=2)
    pending_payments = serializers.IntegerField()


class DashboardPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer(allow_null=True)
    current_term = TermSerializer(allow_null=True)
    announcements = AcademicAnnouncementSerializer(many=True)
    debt_summary = DebtSummarySerializer()
    enrolled_courses = TranscriptSerializer(many=True)


class SemesterTranscriptPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    term = TermSerializer(allow_null=True)
    transcripts = TranscriptSerializer(many=True)
    current_term_gpa = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)


class FullTranscriptPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    gpa = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    taken_units = serializers.IntegerField()
    transcripts = TranscriptSerializer(many=True)


class GradesPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    exam_results = ExamResultSerializer(many=True)
    transcripts = TranscriptSerializer(many=True)


class CourseSelectionPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer(allow_null=True)
    term = TermSerializer()
    available_offers = ClassOfferSerializer(many=True)
    taken_units = serializers.IntegerField()


class AddDropPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    term = TermSerializer(allow_null=True)
    enrolled_courses = TranscriptSerializer(many=True)


class FinancialPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    payment_type = serializers.CharField()
    total_paid = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=20, decimal_places=2)
    payments = StudentPaymentsSerializer(many=True)


class PaymentHistoryPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    payments = StudentPaymentsSerializer(many=True)


class LoanListPageResponseSerializer(serializers.Serializer):
    loans = LoanSerializer(many=True)


class StudentRequestsPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    requests = StudentRequestSerializer(many=True)


class LeaveRequestPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    leave_requests = AcademicLeaveRequestSerializer(many=True)


class TeacherPageEntrySerializer(TeacherSerializer):
    research_interests = serializers.ListField(child=serializers.CharField(), read_only=True)
    recent_classes = ClassOfferSerializer(many=True, read_only=True)


class TeachersPageResponseSerializer(serializers.Serializer):
    teachers = TeacherPageEntrySerializer(many=True)


class GradeObjectionPageResponseSerializer(serializers.Serializer):
    student = StudentBriefSerializer()
    exam_results = ExamResultSerializer(many=True)
    objections = StudentRequestSerializer(many=True)
