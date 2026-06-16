"""Idempotent demo data for API testing and frontend development."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from core.models import (
    AcademicAnnouncement,
    AcademicEvent,
    AcademicLeaveRequest,
    AcademicProgram,
    Attendance,
    AuthAccount,
    AuthRole,
    Book,
    Class,
    ClassOffer,
    Company,
    ConstValue,
    Department,
    DocumentStudent,
    EducationBranch,
    EmailAddress,
    Employee,
    Exam,
    ExamInvigilator,
    ExamResult,
    Internship,
    Lesson,
    LibraryBookLending,
    LibraryResource,
    Loan,
    Person,
    PersonSkill,
    PhoneNumber,
    PostalAddress,
    PrerequisiteWarning,
    Scholarship,
    Student,
    StudentPayments,
    StudentRequest,
    Teacher,
    TeacherEvaluation,
    TeacherResearchInterest,
    Tendency,
    Term,
    Transcript,
    DormitoryRequest,
)

DEMO_PASSWORD = "demo1234"
SECURITY_ANSWER = "tehran"


def _cv(code, caption, **defaults):
    obj, _ = ConstValue.objects.get_or_create(
        code=code,
        defaults={"caption": caption, "is_active": True, **defaults},
    )
    return obj


def _person(username, first_name, last_name, national_code):
    person, created = Person.objects.get_or_create(
        username=username,
        defaults={
            "password": make_password(DEMO_PASSWORD),
            "national_code": national_code,
            "first_name": first_name,
            "last_name": last_name,
            "security_question": "birth_city",
            "security_answer": SECURITY_ANSWER,
        },
    )
    if not created:
        person.password = make_password(DEMO_PASSWORD)
        person.security_question = "birth_city"
        person.security_answer = SECURITY_ANSWER
        person.save(update_fields=["password", "security_question", "security_answer"])
    return person


def _account(person, username, email, role_codes):
    account, _ = AuthAccount.objects.update_or_create(
        username=username,
        defaults={
            "person": person,
            "email": email,
            "password_hash": make_password(DEMO_PASSWORD),
        },
    )
    roles = list(AuthRole.objects.filter(code__in=role_codes))
    account.roles.set(roles)
    return account


def seed_demo_data(stdout=None):
    """Populate all demo records; safe to run multiple times."""
    write = stdout.write if stdout else print

    # --- Roles ---
    role_defs = [
        ("admin", "مدیر سیستم"),
        ("staff", "کارمند اداری"),
        ("student", "دانشجو"),
        ("teacher", "استاد"),
        ("employee", "کارمند"),
    ]
    for code, name in role_defs:
        AuthRole.objects.get_or_create(code=code, defaults={"name": name})

    # --- ConstValue lookup rows ---
    cv_request_type = _cv("req_type_leave", "درخواست مرخصی")
    cv_grade_objection = _cv("grade_objection", "اعتراض به نمره")
    cv_request_status_pending = _cv("req_status_pending", "در انتظار بررسی")
    cv_request_status_approved = _cv("req_status_approved", "تایید شده")
    cv_doc_type = _cv("doc_type_id_card", "کارت ملی")
    cv_doc_verify = _cv("doc_verify_pending", "در انتظار تایید")
    cv_event_type = _cv("event_type_workshop", "کارگاه آموزشی")
    cv_event_status = _cv("event_status_active", "فعال")
    cv_ann_type = _cv("ann_type_general", "اطلاعیه عمومی")
    cv_ann_audience = _cv("ann_audience_students", "دانشجویان")
    cv_ann_status = _cv("ann_status_active", "فعال", is_active=True)
    cv_blood = _cv("blood_o_pos", "O+")
    cv_class_type = _cv("class_type_theory", "نظری")
    cv_lending_status = _cv("lending_active", "امانت فعال")
    cv_position = _cv("emp_position_clerk", "کارشناس اداری")
    cv_shift = _cv("emp_shift_morning", "صبح")
    cv_employment = _cv("emp_type_fulltime", "تمام‌وقت")
    cv_lesson_lang = _cv("lesson_lang_fa", "فارسی")

    # --- Lookup hierarchy ---
    dept, _ = Department.objects.get_or_create(
        department_code="DEMO",
        defaults={"department_title": "دانشکده مهندسی کامپیوتر (نمونه)"},
    )
    branch, _ = EducationBranch.objects.get_or_create(
        title="مهندسی نرم‌افزار",
        department=dept,
        defaults={"degree_level": "bachelor"},
    )
    tendency, _ = Tendency.objects.get_or_create(
        tendency_code=101,
        defaults={
            "tendency_name": "نرم‌افزار",
            "field": branch,
            "total_units": 140,
            "is_active": True,
        },
    )

    now = timezone.now()
    Term.objects.filter(is_current=True).update(is_current=False)
    past_term, _ = Term.objects.update_or_create(
        term_id=14031,
        defaults={
            "term_title": "نیمسال اول 1403",
            "start_term": date(2024, 9, 23),
            "end_term": date(2025, 2, 19),
            "is_current": False,
            "registration_start": now - timedelta(days=365),
            "name": "1403-1",
        },
    )
    current_term, _ = Term.objects.update_or_create(
        term_id=14041,
        defaults={
            "term_title": "نیمسال اول 1404",
            "start_term": date(2025, 9, 23),
            "end_term": date(2026, 2, 19),
            "is_current": True,
            "registration_start": now - timedelta(days=30),
            "name": "1404-1",
        },
    )

    # --- Demo persons & accounts ---
    student_person = _person("demo_student", "دانشجو", "نمونه", "0012345678")
    teacher_person = _person("demo_teacher", "استاد", "نمونه", "0022345678")
    staff_person = _person("demo_staff", "کارمند", "نمونه", "0032345678")
    admin_person = _person("demo_admin", "مدیر", "نمونه", "0042345678")
    extra_person = _person("demo_extra", "شخص", "اضافی", "0052345678")

    student_account = _account(student_person, "demo_student", "demo@ntbiau.ac.ir", ["student"])
    _account(teacher_person, "demo_teacher", "teacher@ntbiau.ac.ir", ["teacher"])
    _account(staff_person, "demo_staff", "staff@ntbiau.ac.ir", ["staff", "employee"])
    _account(admin_person, "demo_admin", "admin@ntbiau.ac.ir", ["admin"])

    # --- Contact info for demo_student ---
    PhoneNumber.objects.get_or_create(person=student_person, phone="09121234567")
    EmailAddress.objects.get_or_create(
        person=student_person,
        email="student.personal@example.com",
        defaults={"email_type": "personal", "is_primary": True},
    )
    PersonSkill.objects.get_or_create(
        person=student_person,
        name="Python",
        defaults={"level": "intermediate"},
    )
    PostalAddress.objects.get_or_create(
        person=student_person,
        defaults={
            "address_detail": "تهران، خیابان آزادی، پلاک ۱۰",
            "city": "تهران",
            "postal_code": "1234567890",
        },
    )

    # --- Profiles ---
    teacher, _ = Teacher.objects.get_or_create(
        person=teacher_person,
        defaults={"full_name": "دکتر استاد نمونه"},
    )
    TeacherResearchInterest.objects.get_or_create(
        teacher=teacher,
        defaults={"research_interest": "هوش مصنوعی و یادگیری ماشین"},
    )

    employee, _ = Employee.objects.get_or_create(
        person=staff_person,
        defaults={
            "department": dept,
            "position": cv_position,
            "work_shift": cv_shift,
            "employment_type": cv_employment,
            "employee_code": "EMP001",
            "personnel_code": "EMP001",
            "hire_date": date(2020, 3, 21),
            "is_active": True,
        },
    )

    student, _ = Student.objects.update_or_create(
        student_number="1400123456",
        defaults={
            "person": student_person,
            "department": dept,
            "branch": branch,
            "tendency": tendency,
            "education_branch": branch,
            "advisor_teacher": teacher,
            "blood_type": cv_blood,
            "entry_year": 1400,
            "military_status": "studying",
            "payment_type": "end_of_term",
            "is_active": True,
            "gpa": Decimal("17.25"),
            "current_term_gpa": 18.5,
            "taken_units": 12,
        },
    )

    # --- Lessons & classes ---
    lesson_base, _ = Lesson.objects.get_or_create(
        lesson_code="DEMO101",
        defaults={
            "title": "مبانی برنامه‌نویسی",
            "units": 3,
            "department": dept,
            "education_branch": branch,
            "theoretical_units": 2,
            "practical_units": 1,
            "lesson_language": cv_lesson_lang,
            "is_active": True,
        },
    )
    lesson_adv, _ = Lesson.objects.get_or_create(
        lesson_code="DEMO201",
        defaults={
            "title": "ساختمان داده",
            "units": 3,
            "department": dept,
            "education_branch": branch,
            "theoretical_units": 3,
            "lesson_language": cv_lesson_lang,
            "is_active": True,
        },
    )
    lesson_elective, _ = Lesson.objects.get_or_create(
        lesson_code="DEMO301",
        defaults={
            "title": "هوش مصنوعی",
            "units": 3,
            "department": dept,
            "education_branch": branch,
            "theoretical_units": 2,
            "practical_units": 1,
            "lesson_language": cv_lesson_lang,
            "is_active": True,
        },
    )
    if not lesson_adv.prerequisites.filter(pk=lesson_base.pk).exists():
        lesson_adv.prerequisites.add(lesson_base)

    class1, _ = Class.objects.get_or_create(
        class_number="DEMO-C01",
        term=current_term,
        lesson=lesson_base,
        defaults={
            "max_capacity": 30,
            "tendency": tendency,
            "class_location": "کلاس ۱۰۱",
            "class_type": cv_class_type,
            "class_day": "شنبه",
        },
    )
    class2, _ = Class.objects.get_or_create(
        class_number="DEMO-C02",
        term=current_term,
        lesson=lesson_elective,
        defaults={
            "max_capacity": 25,
            "tendency": tendency,
            "class_location": "کلاس ۲۰۲",
            "class_type": cv_class_type,
            "class_day": "دوشنبه",
        },
    )
    past_class, _ = Class.objects.get_or_create(
        class_number="DEMO-C00",
        term=past_term,
        lesson=lesson_base,
        defaults={"max_capacity": 30, "tendency": tendency, "class_location": "کلاس ۱۰۱"},
    )

    offer1, _ = ClassOffer.objects.get_or_create(
        class_group=class1,
        term=current_term,
        defaults={"teacher": teacher},
    )
    offer2, _ = ClassOffer.objects.get_or_create(
        class_group=class2,
        term=current_term,
        defaults={"teacher": teacher},
    )
    past_offer, _ = ClassOffer.objects.get_or_create(
        class_group=past_class,
        term=past_term,
        defaults={"teacher": teacher},
    )

    Transcript.objects.update_or_create(
        student=student,
        class_offer=offer1,
        defaults={"final_grade": Decimal("18.00"), "pass_status": True},
    )
    Transcript.objects.update_or_create(
        student=student,
        class_offer=offer2,
        defaults={"final_grade": Decimal("17.50"), "pass_status": True},
    )
    Transcript.objects.update_or_create(
        student=student,
        class_offer=past_offer,
        defaults={"final_grade": Decimal("16.00"), "pass_status": True},
    )

    exam1, _ = Exam.objects.get_or_create(
        class_offer=offer1,
        exam_type="میان‌ترم",
        exam_date=date(2025, 11, 15),
        defaults={"exam_location": "سالن A", "exam_duration": 90},
    )
    ExamResult.objects.update_or_create(
        student=student,
        exam=exam1,
        defaults={"score": Decimal("17.00"), "status": "قبول"},
    )
    ExamInvigilator.objects.get_or_create(exam=exam1, employee=employee)

    Attendance.objects.update_or_create(
        student=student,
        class_offer=offer1,
        session_number=1,
        defaults={"attendance_status": "حاضر"},
    )
    Attendance.objects.update_or_create(
        student=student,
        class_offer=offer1,
        session_number=2,
        defaults={"attendance_status": "غایب", "absence_description": "مریضی"},
    )

    TeacherEvaluation.objects.update_or_create(
        teacher=teacher,
        student=student,
        term=current_term,
        defaults={"teaching_quality": 5, "comment": "تدریس عالی"},
    )

    PrerequisiteWarning.objects.update_or_create(
        student=student,
        lesson=lesson_adv,
        term=current_term,
        defaults={
            "prerequisite_avg": 11.5,
            "min_pass_threshold": 12.0,
            "created_by": admin_person,
            "is_active": True,
        },
    )

    # --- Finance ---
    StudentPayments.objects.update_or_create(
        tracking_code="DEMO00000001",
        defaults={
            "student": student,
            "amount": 5_000_000,
            "payment_datetime": now - timedelta(days=10),
            "is_confirmed": True,
            "reference_bank": "ملت",
        },
    )
    StudentPayments.objects.update_or_create(
        tracking_code="DEMO00000002",
        defaults={
            "student": student,
            "amount": 2_000_000,
            "payment_datetime": now - timedelta(days=2),
            "is_confirmed": False,
            "reference_bank": "ملی",
        },
    )

    StudentRequest.objects.update_or_create(
        student=student,
        request_type=cv_request_type,
        description="درخواست تمدید مهلت تحویل پروژه",
        defaults={
            "request_date": date.today(),
            "status": cv_request_status_pending,
            "employee_follower": employee,
        },
    )

    StudentRequest.objects.update_or_create(
        student=student,
        request_type=cv_grade_objection,
        description="اعتراض به نمره میان‌ترم مبانی برنامه‌نویسی",
        defaults={
            "request_date": date.today(),
            "status": cv_request_status_pending,
            "employee_follower": employee,
        },
    )

    AcademicLeaveRequest.objects.get_or_create(
        student=student,
        leave_reason="مرخصی تحصیلی یک نیمسال به دلیل مسائل شخصی",
        defaults={"is_approved": False},
    )

    Scholarship.objects.update_or_create(
        student=student,
        title="بورسیه شایستگی تحصیلی",
        defaults={"amount": 3_000_000, "status": "approved"},
    )

    DormitoryRequest.objects.get_or_create(
        student=student,
        room_type="2_person",
        defaults={"approval_status": "pending"},
    )

    Loan.objects.update_or_create(
        loan_file_number="DEMO-LOAN-001",
        defaults={
            "borrower": student_person,
            "amount": 50_000_000,
            "loan_status": "active",
            "loan_request_date": now - timedelta(days=60),
            "loan_type": "وام تحصیلی",
            "amount_of_each_loan_installment": 5_000_000,
            "loan_repayment_period": 10,
            "loan_installment_date": date.today() + timedelta(days=30),
            "number_of_loan_installments": 10,
            "how_to_pay_loan_installments": "کسر از حقوق / واریز بانکی",
        },
    )

    # --- Library & misc ---
    book, _ = Book.objects.get_or_create(
        isbn="978-964-DEMO01",
        defaults={"title": "الگوریتم‌ها — نمونه"},
    )
    LibraryBookLending.objects.get_or_create(
        book=book,
        student=student,
        defaults={
            "employee": employee,
            "status": cv_lending_status,
            "due_date": now + timedelta(days=14),
            "is_returned": False,
        },
    )
    LibraryResource.objects.get_or_create(
        person=student_person,
        resource_name="کتاب مرجع پایگاه داده",
        defaults={"is_returned": False},
    )

    company, _ = Company.objects.get_or_create(
        registration_number="DEMO-CO-001",
        defaults={"name": "شرکت فناوری نمونه"},
    )
    Internship.objects.get_or_create(
        student=student,
        company=company,
        defaults={
            "start_date": date(2025, 7, 1),
            "finish_date": date(2025, 9, 1),
            "evaluation_score": Decimal("18.00"),
        },
    )

    DocumentStudent.objects.get_or_create(
        student=student,
        document_type=cv_doc_type,
        defaults={"verification_status": cv_doc_verify},
    )

    AcademicProgram.objects.get_or_create(
        program_title="برنامه کارشناسی نرم‌افزار (نمونه)",
        department=dept,
        defaults={
            "degree_level": "bachelor",
            "start_programtime": date(2020, 9, 23),
            "finish_programtime": date(2024, 9, 22),
        },
    )

    AcademicEvent.objects.get_or_create(
        title_fa="کارگاه برنامه‌نویسی پایتون",
        event_type=cv_event_type,
        start_date=date.today() + timedelta(days=7),
        defaults={
            "end_date": date.today() + timedelta(days=7),
            "location": "آمفی‌تئاتر دانشکده",
            "status": cv_event_status,
            "organizer_person": teacher_person,
            "host_department": dept,
            "is_public": True,
        },
    )

    AcademicAnnouncement.objects.get_or_create(
        title="شروع ثبت‌نام نیمسال جاری",
        defaults={
            "body": "ثبت‌نام نیمسال اول 1404 از تاریخ ۱ مهر آغاز می‌شود.",
            "announcement_type": cv_ann_type,
            "audience": cv_ann_audience,
            "status": cv_ann_status,
            "creator": admin_person,
            "is_urgent": True,
            "summary": "اطلاعیه ثبت‌نام",
            "department_code": dept.department_code,
        },
    )

    write("")
    write("=" * 60)
    write("Demo data seeded successfully (idempotent).")
    write("=" * 60)
    write("")
    write("Accounts (password: demo1234):")
    write("  demo_student  — student role")
    write("  demo_teacher  — teacher role")
    write("  demo_staff    — staff + employee roles")
    write("  demo_admin    — admin role")
    write("")
    write("Security answer (password reset): tehran")
    write("")
    write("Key IDs:")
    write(f"  student_number: {student.student_number}")
    write(f"  current_term:   {current_term.term_id} ({current_term.term_title})")
    write("  payment track:  DEMO00000001")
    write(f"  loan file:      DEMO-LOAN-001")
    write("")
    write("Login: POST /api/v1/auth/login/")
    write("Auth:  Authorization: Token <session_key>")
    write("")

    return {
        "student_account": student_account,
        "student": student,
        "current_term": current_term,
        "dept": dept,
    }
