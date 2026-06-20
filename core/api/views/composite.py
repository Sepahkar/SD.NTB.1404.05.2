from django.db.models import Sum
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.openapi.tags import TAG_COMPOSITE_PAGES
from core.api.permissions import IsAuthenticatedAccount
from core.api.serializers.composite_pages import (
    AddDropPageResponseSerializer,
    CourseSelectionPageResponseSerializer,
    DashboardPageResponseSerializer,
    FinancialPageResponseSerializer,
    FullTranscriptPageResponseSerializer,
    GradeObjectionPageResponseSerializer,
    GradesPageResponseSerializer,
    LeaveRequestPageResponseSerializer,
    LoanListPageResponseSerializer,
    PaymentHistoryPageResponseSerializer,
    SemesterTranscriptPageResponseSerializer,
    StudentRequestsPageResponseSerializer,
    TeachersPageResponseSerializer,
)
from core.api.serializers.academic import TranscriptSerializer
from core.api.serializers.finance import (
    AcademicLeaveRequestSerializer,
    LoanSerializer,
    StudentRequestSerializer,
)
from core.services import page_data as pd


def _get_current_student(request):
    person = request.user.person
    if not hasattr(person, "student_profile"):
        return None
    return person.student_profile


def _require_student_response(request):
    student = _get_current_student(request)
    if not student:
        return None, Response(
            {"detail": "پروفایل دانشجو یافت نشد."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return student, None


EnrollRequestSerializer = inline_serializer(
    name="CourseEnrollRequest",
    fields={"class_offer_id": serializers.IntegerField()},
)

DropRequestSerializer = inline_serializer(
    name="CourseDropRequest",
    fields={"transcript_id": serializers.IntegerField()},
)


class DashboardPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="داشبورد اصلی — داده ترکیبی",
        responses={200: DashboardPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_dashboard_data(student))


class SemesterTranscriptPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="کارنامه نیمسال جاری",
        responses={200: SemesterTranscriptPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_semester_transcript_data(student))


class FullTranscriptPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="کارنامه کل",
        responses={200: FullTranscriptPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_full_transcript_data(student))


class GradesPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="کارنامه و نمرات",
        responses={200: GradesPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_grades_data(student))


class CourseSelectionPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="پنل انتخاب واحد",
        responses={200: CourseSelectionPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        data = pd.get_course_selection_data(student)
        if data is None:
            return Response({"detail": "ترم جاری تعریف نشده."}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="پنل انتخاب واحد — ثبت‌نام",
        request=EnrollRequestSerializer,
        responses={201: TranscriptSerializer},
    )
    def post(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        class_offer_id = request.data.get("class_offer_id")
        if not class_offer_id:
            return Response({"detail": "class_offer_id الزامی است."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = pd.enroll_student_in_offer(student, class_offer_id)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_201_CREATED)


class AddDropPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="حذف و اضافه",
        responses={200: AddDropPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_add_drop_data(student))

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="حذف و اضافه — حذف درس",
        request=DropRequestSerializer,
        responses={200: inline_serializer(name="DropResponse", fields={"detail": serializers.CharField()})},
    )
    def post(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        transcript_id = request.data.get("transcript_id")
        if not transcript_id:
            return Response({"detail": "transcript_id الزامی است."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = pd.drop_student_course(student, transcript_id)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class FinancialPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="امور مالی / بدهی‌ها",
        responses={200: FinancialPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_financial_data(student))


class PaymentHistoryPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="تاریخچه پرداخت‌ها",
        responses={200: PaymentHistoryPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_payment_history_data(student))


class LoanRequestPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست وام — فهرست",
        responses={200: LoanListPageResponseSerializer},
    )
    def get(self, request):
        return Response(pd.get_loans_data(request.user.person))

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست وام — ثبت",
        request=LoanSerializer,
        responses={201: LoanSerializer},
    )
    def post(self, request):
        loan = pd.create_loan_for_person(request.user.person, request.data)
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


class StudentRequestsPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست‌های دانشجو — فهرست",
        responses={200: StudentRequestsPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_student_requests_data(student))

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست‌های دانشجو — ثبت",
        request=StudentRequestSerializer,
        responses={201: StudentRequestSerializer},
    )
    def post(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        req = pd.create_student_request(student, request.data)
        return Response(StudentRequestSerializer(req).data, status=status.HTTP_201_CREATED)


class LeaveRequestPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست مرخصی — فهرست",
        responses={200: LeaveRequestPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_leave_requests_data(student))

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست مرخصی — ثبت",
        request=AcademicLeaveRequestSerializer,
        responses={201: AcademicLeaveRequestSerializer},
    )
    def post(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        leave = pd.create_leave_request(student, request.data)
        return Response(AcademicLeaveRequestSerializer(leave).data, status=status.HTTP_201_CREATED)


class TeachersPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="معرفی اساتید",
        responses={200: TeachersPageResponseSerializer},
    )
    def get(self, request):
        return Response(pd.get_teachers_data())


class GradeObjectionPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="اعتراض به نمره — فهرست",
        responses={200: GradeObjectionPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        return Response(pd.get_grade_objection_data(student))

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="اعتراض به نمره — ثبت",
        request=StudentRequestSerializer,
        responses={201: StudentRequestSerializer},
    )
    def post(self, request):
        student, error = _require_student_response(request)
        if error:
            return error
        req = pd.create_student_request(student, request.data)
        return Response(StudentRequestSerializer(req).data, status=status.HTTP_201_CREATED)
