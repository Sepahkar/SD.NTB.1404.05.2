"""Shared page data queries for composite API views and Django template views."""

from django.db.models import Sum
from django.utils import timezone

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
from core.api.serializers.lookup import TermSerializer
from core.api.serializers.profiles import StudentBriefSerializer, TeacherSerializer
from core.models import (
    AcademicAnnouncement,
    AcademicLeaveRequest,
    ClassOffer,
    ExamResult,
    Loan,
    StudentPayments,
    StudentRequest,
    Teacher,
    Term,
    Transcript,
)


def get_current_term():
    return Term.objects.filter(is_current=True).first()


def debt_summary(student):
    confirmed = StudentPayments.objects.filter(student=student, is_confirmed=True).aggregate(
        total=Sum("amount")
    )["total"] or 0
    pending = StudentPayments.objects.filter(student=student, is_confirmed=False).count()
    return {"total_paid": confirmed, "pending_payments": pending}


def enrolled_courses(student, term):
    if not term:
        return []
    transcripts = Transcript.objects.filter(
        student=student, class_offer__term=term
    ).select_related(
        "class_offer",
        "class_offer__class_group",
        "class_offer__class_group__lesson",
        "class_offer__teacher",
        "class_offer__teacher__person",
    )
    return TranscriptSerializer(transcripts, many=True).data


def get_dashboard_data(student):
    current_term = get_current_term()
    announcements = AcademicAnnouncement.objects.filter(status__is_active=True).order_by(
        "-is_urgent", "-publish_date"
    )[:10]
    payments = StudentPayments.objects.filter(student=student).order_by("-payment_datetime")
    pending_amount = payments.filter(is_confirmed=False).aggregate(total=Sum("amount"))["total"] or 0
    return {
        "student": StudentBriefSerializer(student).data,
        "current_term": TermSerializer(current_term).data if current_term else None,
        "announcements": AcademicAnnouncementSerializer(announcements, many=True).data,
        "debt_summary": {
            **debt_summary(student),
            "total_pending_amount": pending_amount,
            "term_tuition": 25_000_000,
        },
        "enrolled_courses": enrolled_courses(student, current_term),
        "recent_payments": StudentPaymentsSerializer(payments[:5], many=True).data,
    }


def get_semester_transcript_data(student):
    current_term = get_current_term()
    transcripts = Transcript.objects.filter(student=student)
    if current_term:
        transcripts = transcripts.filter(class_offer__term=current_term)
    transcripts = transcripts.select_related(
        "class_offer", "class_offer__class_group", "class_offer__class_group__lesson"
    )
    return {
        "student": StudentBriefSerializer(student).data,
        "term": TermSerializer(current_term).data if current_term else None,
        "transcripts": TranscriptSerializer(transcripts, many=True).data,
        "current_term_gpa": student.current_term_gpa,
    }


def get_full_transcript_data(student):
    transcripts = (
        Transcript.objects.filter(student=student)
        .select_related("class_offer", "class_offer__term", "class_offer__class_group__lesson")
        .order_by("class_offer__term__start_term")
    )
    return {
        "student": StudentBriefSerializer(student).data,
        "gpa": student.gpa,
        "taken_units": student.taken_units,
        "transcripts": TranscriptSerializer(transcripts, many=True).data,
    }


def get_grades_data(student):
    exam_results = ExamResult.objects.filter(student=student).select_related(
        "exam", "exam__class_offer"
    )
    transcripts = Transcript.objects.filter(student=student).select_related("class_offer")
    return {
        "student": StudentBriefSerializer(student).data,
        "exam_results": ExamResultSerializer(exam_results, many=True).data,
        "transcripts": TranscriptSerializer(transcripts, many=True).data,
    }


def get_course_selection_data(student):
    current_term = get_current_term()
    if not current_term:
        return None
    offers = ClassOffer.objects.filter(term=current_term).select_related(
        "class_group", "class_group__lesson", "teacher", "teacher__person"
    )
    if student.tendency_id:
        offers = offers.filter(class_group__tendency=student.tendency)
    enrolled_ids = Transcript.objects.filter(
        student=student, class_offer__term=current_term
    ).values_list("class_offer_id", flat=True)
    return {
        "student": StudentBriefSerializer(student).data,
        "term": TermSerializer(current_term).data,
        "available_offers": ClassOfferSerializer(offers, many=True).data,
        "enrolled_offer_ids": list(enrolled_ids),
        "taken_units": student.taken_units,
    }


def get_add_drop_data(student):
    current_term = get_current_term()
    transcripts = Transcript.objects.filter(student=student)
    if current_term:
        transcripts = transcripts.filter(class_offer__term=current_term)
    return {
        "student": StudentBriefSerializer(student).data,
        "term": TermSerializer(current_term).data if current_term else None,
        "enrolled_courses": TranscriptSerializer(
            transcripts.select_related(
                "class_offer",
                "class_offer__class_group",
                "class_offer__class_group__lesson",
            ),
            many=True,
        ).data,
    }


def get_financial_data(student):
    payments = StudentPayments.objects.filter(student=student).order_by("-payment_datetime")
    total_paid = payments.filter(is_confirmed=True).aggregate(total=Sum("amount"))["total"] or 0
    total_pending = payments.filter(is_confirmed=False).aggregate(total=Sum("amount"))["total"] or 0
    return {
        "student": StudentBriefSerializer(student).data,
        "payment_type": student.payment_type,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "payments": StudentPaymentsSerializer(payments, many=True).data,
    }


def get_payment_history_data(student):
    payments = StudentPayments.objects.filter(student=student).order_by("-payment_datetime")
    return {
        "student": StudentBriefSerializer(student).data,
        "payments": StudentPaymentsSerializer(payments, many=True).data,
    }


def get_loans_data(person):
    loans = Loan.objects.filter(borrower=person).order_by("-loan_request_date")
    return {"loans": LoanSerializer(loans, many=True).data}


def get_student_requests_data(student):
    requests_qs = StudentRequest.objects.filter(student=student).order_by("-request_date")
    return {
        "student": StudentBriefSerializer(student).data,
        "requests": StudentRequestSerializer(requests_qs, many=True).data,
    }


def get_leave_requests_data(student):
    leaves = AcademicLeaveRequest.objects.filter(student=student).order_by("-request_date")
    return {
        "student": StudentBriefSerializer(student).data,
        "leave_requests": AcademicLeaveRequestSerializer(leaves, many=True).data,
    }


def get_teachers_data():
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
    return {"teachers": result}


def get_grade_objection_data(student):
    exam_results = ExamResult.objects.filter(student=student).select_related("exam")
    objections = StudentRequest.objects.filter(
        student=student, request_type__code="grade_objection"
    )
    return {
        "student": StudentBriefSerializer(student).data,
        "exam_results": ExamResultSerializer(exam_results, many=True).data,
        "objections": StudentRequestSerializer(objections, many=True).data,
    }


def enroll_student_in_offer(student, class_offer_id):
    current_term = get_current_term()
    if not current_term:
        raise ValueError("ترم جاری تعریف نشده.")

    try:
        offer = ClassOffer.objects.select_related("class_group", "term").get(
            pk=class_offer_id, term=current_term
        )
    except ClassOffer.DoesNotExist as exc:
        raise ValueError("کلاس یافت نشد.") from exc

    if student.tendency_id and offer.class_group.tendency_id != student.tendency_id:
        raise ValueError("این کلاس برای گرایش شما نیست.")

    if Transcript.objects.filter(student=student, class_offer=offer).exists():
        raise ValueError("قبلاً در این کلاس ثبت‌نام کرده‌اید.")

    transcript = Transcript.objects.create(student=student, class_offer=offer)
    return TranscriptSerializer(transcript).data


def drop_student_course(student, transcript_id):
    try:
        transcript = Transcript.objects.select_related("class_offer__term").get(
            pk=transcript_id, student=student
        )
    except Transcript.DoesNotExist as exc:
        raise ValueError("رکورد کارنامه یافت نشد.") from exc

    current_term = get_current_term()
    if current_term and transcript.class_offer.term_id != current_term.pk:
        raise ValueError("فقط دروس ترم جاری قابل حذف هستند.")

    transcript.delete()
    return {"detail": "درس با موفقیت حذف شد."}


def create_loan_for_person(person, data):
    payload = dict(data)
    payload["borrower"] = person.pk
    if "loan_request_date" not in payload:
        payload["loan_request_date"] = timezone.now().isoformat()
    if "loan_status" not in payload:
        payload["loan_status"] = "pending"
    if "loan_file_number" not in payload:
        payload["loan_file_number"] = f"WEB-{person.pk}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    serializer = LoanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def create_student_request(student, data):
    payload = dict(data)
    payload["student"] = student.pk
    serializer = StudentRequestSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def create_leave_request(student, data):
    payload = dict(data)
    payload["student"] = student.pk
    serializer = AcademicLeaveRequestSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    return serializer.save()
