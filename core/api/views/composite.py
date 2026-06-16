from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
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
from core.models import (
    AcademicAnnouncement,
    AcademicLeaveRequest,
    ClassOffer,
    ExamResult,
    Loan,
    Student,
    StudentPayments,
    StudentRequest,
    Teacher,
    Term,
    Transcript,
)


def _get_current_student(request):
    person = request.user.person
    if not hasattr(person, "student_profile"):
        return None
    return person.student_profile


def _require_student_response(request):
    """Return 404 Response if the current user has no student profile."""
    student = _get_current_student(request)
    if not student:
        return None, Response(
            {"detail": "پروفایل دانشجو یافت نشد."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return student, None


class DashboardPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="داشبورد اصلی — داده ترکیبی",
        description=(
            "یک درخواست برای صفحه داشبورد: اطلاعات دانشجو، ترم جاری، اطلاعیه‌ها، "
            "خلاصه بدهی و دروس اخذشده. نیاز به احراز هویت دارد."
        ),
        responses={200: DashboardPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        current_term = Term.objects.filter(is_current=True).first()

        announcements = AcademicAnnouncement.objects.filter(
            status__is_active=True,
        ).order_by("-is_urgent", "-publish_date")[:10]

        data = {
            "student": StudentBriefSerializer(student).data,
            "current_term": TermSerializer(current_term).data if current_term else None,
            "announcements": AcademicAnnouncementSerializer(announcements, many=True).data,
            "debt_summary": self._debt_summary(student),
            "enrolled_courses": self._enrolled_courses(student, current_term),
        }
        return Response(data)

    def _debt_summary(self, student):
        confirmed = StudentPayments.objects.filter(student=student, is_confirmed=True).aggregate(
            total=Sum("amount")
        )["total"] or 0
        pending = StudentPayments.objects.filter(student=student, is_confirmed=False).count()
        return {"total_paid": confirmed, "pending_payments": pending}

    def _enrolled_courses(self, student, term):
        if not term:
            return []
        transcripts = Transcript.objects.filter(
            student=student, class_offer__term=term
        ).select_related("class_offer", "class_offer__class_group", "class_offer__teacher")
        return TranscriptSerializer(transcripts, many=True).data


class SemesterTranscriptPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="کارنامه نیمسال جاری",
        description="دریافت کارنامه دانشجو برای نیمسال جاری همراه با معدل نیمسال.",
        responses={200: SemesterTranscriptPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        current_term = Term.objects.filter(is_current=True).first()
        transcripts = Transcript.objects.filter(student=student)
        if current_term:
            transcripts = transcripts.filter(class_offer__term=current_term)

        transcripts = transcripts.select_related(
            "class_offer", "class_offer__class_group", "class_offer__class_group__lesson"
        )
        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "term": TermSerializer(current_term).data if current_term else None,
                "transcripts": TranscriptSerializer(transcripts, many=True).data,
                "current_term_gpa": student.current_term_gpa,
            }
        )


class FullTranscriptPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="کارنامه کل",
        description="دریافت کل سوابق تحصیلی دانشجو شامل معدل کل و واحدهای گذرانده.",
        responses={200: FullTranscriptPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        transcripts = Transcript.objects.filter(student=student).select_related(
            "class_offer", "class_offer__term", "class_offer__class_group__lesson"
        ).order_by("class_offer__term__start_term")

        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "gpa": student.gpa,
                "taken_units": student.taken_units,
                "transcripts": TranscriptSerializer(transcripts, many=True).data,
            }
        )


class GradesPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="کارنامه و نمرات",
        description="دریافت نتایج امتحانات و ریز نمرات کارنامه دانشجو.",
        responses={200: GradesPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        exam_results = ExamResult.objects.filter(student=student).select_related("exam", "exam__class_offer")
        transcripts = Transcript.objects.filter(student=student).select_related("class_offer")

        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "exam_results": ExamResultSerializer(exam_results, many=True).data,
                "transcripts": TranscriptSerializer(transcripts, many=True).data,
            }
        )


class CourseSelectionPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="پنل انتخاب واحد",
        description="لیست کلاس‌های قابل انتخاب در ترم جاری بر اساس گرایش دانشجو.",
        responses={200: CourseSelectionPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        current_term = Term.objects.filter(is_current=True).first()
        if not current_term:
            return Response({"detail": "ترم جاری تعریف نشده."}, status=status.HTTP_404_NOT_FOUND)

        offers = ClassOffer.objects.filter(term=current_term).select_related(
            "class_group", "class_group__lesson", "teacher"
        )
        if student.tendency_id:
            offers = offers.filter(class_group__tendency=student.tendency)

        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "term": TermSerializer(current_term).data,
                "available_offers": ClassOfferSerializer(offers, many=True).data,
                "taken_units": student.taken_units,
            }
        )


class AddDropPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="حذف و اضافه",
        description="دریافت دروس اخذشده دانشجو در ترم جاری برای عملیات حذف و اضافه.",
        responses={200: AddDropPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        current_term = Term.objects.filter(is_current=True).first()
        transcripts = Transcript.objects.filter(student=student)
        if current_term:
            transcripts = transcripts.filter(class_offer__term=current_term)

        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "term": TermSerializer(current_term).data if current_term else None,
                "enrolled_courses": TranscriptSerializer(
                    transcripts.select_related("class_offer"), many=True
                ).data,
            }
        )


class FinancialPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="امور مالی / بدهی‌ها",
        description="خلاصه وضعیت مالی دانشجو: پرداخت‌های تاییدشده، معوق و لیست تراکنش‌ها.",
        responses={200: FinancialPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        payments = StudentPayments.objects.filter(student=student).order_by("-payment_datetime")
        total_paid = payments.filter(is_confirmed=True).aggregate(total=Sum("amount"))["total"] or 0
        total_pending = payments.filter(is_confirmed=False).aggregate(total=Sum("amount"))["total"] or 0

        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "payment_type": student.payment_type,
                "total_paid": total_paid,
                "total_pending": total_pending,
                "payments": StudentPaymentsSerializer(payments, many=True).data,
            }
        )


class PaymentHistoryPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="تاریخچه پرداخت‌ها",
        description="لیست کامل پرداخت‌های دانشجو به ترتیب تاریخ.",
        responses={200: PaymentHistoryPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        payments = StudentPayments.objects.filter(student=student).order_by("-payment_datetime")
        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "payments": StudentPaymentsSerializer(payments, many=True).data,
            }
        )


class LoanRequestPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست وام — فهرست",
        description="دریافت لیست وام‌های درخواست‌شده توسط کاربر جاری.",
        responses={200: LoanListPageResponseSerializer},
    )
    def get(self, request):
        person = request.user.person
        loans = Loan.objects.filter(borrower=person).order_by("-loan_request_date")
        return Response({"loans": LoanSerializer(loans, many=True).data})

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست وام — ثبت",
        description="ثبت درخواست وام جدید برای کاربر جاری.",
        request=LoanSerializer,
        responses={201: LoanSerializer},
    )
    def post(self, request):
        person = request.user.person
        data = request.data.copy()
        data["borrower"] = person.pk
        if "loan_request_date" not in data:
            data["loan_request_date"] = timezone.now().isoformat()
        serializer = LoanSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentRequestsPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست‌های دانشجو — فهرست",
        description="دریافت لیست درخواست‌های ثبت‌شده توسط دانشجو.",
        responses={200: StudentRequestsPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        requests_qs = StudentRequest.objects.filter(student=student).order_by("-request_date")
        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "requests": StudentRequestSerializer(requests_qs, many=True).data,
            }
        )

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست‌های دانشجو — ثبت",
        description="ثبت درخواست جدید برای دانشجوی جاری.",
        request=StudentRequestSerializer,
        responses={201: StudentRequestSerializer},
    )
    def post(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        data = request.data.copy()
        data["student"] = student.pk
        serializer = StudentRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LeaveRequestPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست مرخصی — فهرست",
        description="دریافت لیست درخواست‌های مرخصی تحصیلی دانشجو.",
        responses={200: LeaveRequestPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        leaves = AcademicLeaveRequest.objects.filter(student=student).order_by("-request_date")
        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "leave_requests": AcademicLeaveRequestSerializer(leaves, many=True).data,
            }
        )

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="درخواست مرخصی — ثبت",
        description="ثبت درخواست مرخصی تحصیلی جدید.",
        request=AcademicLeaveRequestSerializer,
        responses={201: AcademicLeaveRequestSerializer},
    )
    def post(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        data = request.data.copy()
        data["student"] = student.pk
        serializer = AcademicLeaveRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TeachersPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="معرفی اساتید",
        description="لیست اساتید همراه با علایق پژوهشی و کلاس‌های اخیر.",
        responses={200: TeachersPageResponseSerializer},
    )
    def get(self, request):
        teachers = Teacher.objects.select_related("person").prefetch_related("research_interests").all()
        result = []
        for teacher in teachers:
            item = TeacherSerializer(teacher).data
            item["research_interests"] = list(
                teacher.research_interests.values_list("research_interest", flat=True)
            )
            offers = ClassOffer.objects.filter(teacher=teacher).select_related(
                "class_group__lesson", "term"
            )[:5]
            item["recent_classes"] = ClassOfferSerializer(offers, many=True).data
            result.append(item)
        return Response({"teachers": result})


class GradeObjectionPageAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="اعتراض به نمره — فهرست",
        description="دریافت نتایج امتحان و اعتراضات ثبت‌شده دانشجو.",
        responses={200: GradeObjectionPageResponseSerializer},
    )
    def get(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        exam_results = ExamResult.objects.filter(student=student).select_related("exam")
        objections = StudentRequest.objects.filter(
            student=student, request_type__code="grade_objection"
        )
        return Response(
            {
                "student": StudentBriefSerializer(student).data,
                "exam_results": ExamResultSerializer(exam_results, many=True).data,
                "objections": StudentRequestSerializer(objections, many=True).data,
            }
        )

    @extend_schema(
        tags=[TAG_COMPOSITE_PAGES],
        summary="اعتراض به نمره — ثبت",
        description="ثبت درخواست اعتراض به نمره برای دانشجوی جاری.",
        request=StudentRequestSerializer,
        responses={201: StudentRequestSerializer},
    )
    def post(self, request):
        student, error = _require_student_response(request)
        if error:
            return error

        data = request.data.copy()
        data["student"] = student.pk
        serializer = StudentRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
