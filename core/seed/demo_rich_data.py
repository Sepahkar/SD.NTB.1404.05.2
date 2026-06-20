"""Rich demo dataset for demo_student — realistic Persian university data."""

from datetime import date, time, timedelta
from decimal import Decimal

from django.utils import timezone

from core.models import (
    AcademicAnnouncement,
    Class,
    ClassOffer,
    Exam,
    ExamResult,
    Lesson,
    Person,
    Student,
    StudentPayments,
    Teacher,
    TeacherResearchInterest,
    Term,
    Transcript,
)


def enrich_demo_student(ctx, write=None):
    """Add abundant realistic records for demo_student dashboard and pages."""
    write = write or (lambda x: None)
    student = ctx["student"]
    dept = ctx["dept"]
    branch = ctx["branch"]
    tendency = ctx["tendency"]
    current_term = ctx["current_term"]
    past_term = ctx.get("past_term")
    cv_class_type = ctx["cv_class_type"]
    cv_lesson_lang = ctx["cv_lesson_lang"]
    cv_ann_type = ctx["cv_ann_type"]
    cv_ann_audience = ctx["cv_ann_audience"]
    cv_ann_status = ctx["cv_ann_status"]
    admin_person = ctx["admin_person"]
    now = timezone.now()

    person = student.person
    person.first_name = "الهه"
    person.last_name = "هاشم‌آبادی"
    person.full_name = "الهه هاشم‌آبادی"
    person.gender = "female"
    person.birth_date = date(2002, 5, 14)
    person.save()

    # --- Extra terms ---
    term_14032, _ = Term.objects.update_or_create(
        term_id=14032,
        defaults={
            "term_title": "نیمسال دوم 1403",
            "start_term": date(2025, 2, 20),
            "end_term": date(2025, 7, 20),
            "is_current": False,
            "registration_start": now - timedelta(days=200),
            "name": "1403-2",
        },
    )
    term_14033, _ = Term.objects.update_or_create(
        term_id=14033,
        defaults={
            "term_title": "تابستان 1404",
            "start_term": date(2025, 7, 21),
            "end_term": date(2025, 9, 21),
            "is_current": False,
            "registration_start": now - timedelta(days=120),
            "name": "1404-summer",
        },
    )

    teachers_spec = [
        ("demo_teacher_01", "محمد", "سپه‌کار", "هوش مصنوعی و یادگیری عمیق"),
        ("demo_teacher_02", "علی", "رضایی", "پایگاه داده و Big Data"),
        ("demo_teacher_03", "یاسین", "اکبری", "بازی‌سازی و گرافیک"),
        ("demo_teacher_04", "نازنین", "ملکی", "مهندسی وب و Cloud"),
        ("demo_teacher_05", "زینب", "خانی", "ریاضیات گسسته"),
        ("demo_teacher_06", "قاسم", "رستمی", "معارف اسلامی"),
        ("demo_teacher_07", "فاطمه", "مرادی", "شبکه‌های کامپیوتری"),
        ("demo_teacher_08", "رضا", "کریمی", "سیستم‌عامل"),
    ]
    teachers = []
    for idx, (uname, fn, ln, interest) in enumerate(teachers_spec):
        tp, _ = Person.objects.get_or_create(
            username=uname,
            defaults={
                "national_code": f"100234567{idx}",
                "first_name": fn,
                "last_name": ln,
                "full_name": f"دکتر {fn} {ln}",
            },
        )
        t, _ = Teacher.objects.get_or_create(
            person=tp,
            defaults={"full_name": f"دکتر {fn} {ln}"},
        )
        TeacherResearchInterest.objects.get_or_create(
            teacher=t, defaults={"research_interest": interest}
        )
        teachers.append(t)

    lessons_spec = [
        ("DEMO101", "مبانی برنامه‌نویسی", 3, 2, 1),
        ("DEMO201", "ساختمان داده", 3, 3, 0),
        ("DEMO301", "هوش مصنوعی", 3, 2, 1),
        ("DEMO401", "توسعه نرم‌افزار", 3, 2, 1),
        ("DEMO402", "آزمون نرم‌افزار", 3, 3, 0),
        ("DEMO403", "پایگاه داده", 3, 2, 1),
        ("DEMO404", "بازی‌سازی", 3, 2, 1),
        ("DEMO405", "مهندسی اینترنت", 3, 3, 0),
        ("DEMO406", "ریاضیات گسسته", 3, 3, 0),
        ("DEMO407", "اندیشه اسلامی ۱", 2, 2, 0),
        ("DEMO408", "سیستم‌عامل", 3, 3, 0),
        ("DEMO409", "شبکه‌های کامپیوتری", 3, 2, 1),
        ("DEMO410", "طراحی کامپایلر", 3, 3, 0),
        ("DEMO411", "مبانی رایانه", 3, 2, 1),
        ("DEMO412", "برنامه‌نویسی پیشرفته", 3, 2, 1),
        ("DEMO413", "امنیت شبکه", 3, 3, 0),
        ("DEMO414", "پروژه نرم‌افزار", 3, 1, 2),
    ]
    schedule = [
        ("شنبه", "A129", time(7, 30)),
        ("یکشنبه", "A127", time(7, 30)),
        ("دوشنبه", "A130", time(14, 40)),
        ("سه‌شنبه", "A125", time(10, 15)),
        ("چهارشنبه", "A126", time(13, 0)),
        ("شنبه", "A131", time(10, 0)),
        ("یکشنبه", "A128", time(13, 0)),
    ]

    lessons = []
    for i, (code, title, units, th, pr) in enumerate(lessons_spec):
        lesson, _ = Lesson.objects.get_or_create(
            lesson_code=code,
            defaults={
                "title": title,
                "units": units,
                "department": dept,
                "education_branch": branch,
                "theoretical_units": th,
                "practical_units": pr,
                "lesson_language": cv_lesson_lang,
                "is_active": True,
            },
        )
        lessons.append(lesson)

    def _class_for(lesson, term, teacher, day, loc, t, num):
        cls, _ = Class.objects.get_or_create(
            class_number=num,
            term=term,
            lesson=lesson,
            defaults={
                "max_capacity": 35,
                "tendency": tendency,
                "class_location": loc,
                "class_type": cv_class_type,
                "class_day": day,
                "class_time": t,
            },
        )
        offer, _ = ClassOffer.objects.get_or_create(
            class_group=cls, term=term, defaults={"teacher": teacher}
        )
        return offer

    current_offers = []
    for i, lesson in enumerate(lessons[:7]):
        day, loc, t = schedule[i % len(schedule)]
        teacher = teachers[i % len(teachers)]
        offer = _class_for(
            lesson, current_term, teacher, day, loc, t, f"1404-C{i+1:02d}"
        )
        current_offers.append(offer)

    past_terms = [past_term, term_14032, term_14033]
    past_grades = [16.0, 17.0, 18.0, 17.5, 16.5, 19.0, 15.5, 18.5, 17.0, 16.0]
    gi = 0
    for term in past_terms:
        if not term:
            continue
        for j, lesson in enumerate(lessons[7:14]):
            teacher = teachers[(j + 2) % len(teachers)]
            offer = _class_for(
                lesson, term, teacher, "شنبه", f"B{100+j}", time(8, 0), f"{term.term_id}-C{j+1}"
            )
            grade = Decimal(str(past_grades[gi % len(past_grades)]))
            gi += 1
            Transcript.objects.update_or_create(
                student=student,
                class_offer=offer,
                defaults={"final_grade": grade, "pass_status": grade >= 10},
            )
            exam, _ = Exam.objects.get_or_create(
                class_offer=offer,
                exam_type="پایان‌ترم",
                exam_date=term.end_term or date.today(),
                defaults={"exam_location": "سالن امتحانات", "exam_duration": 120},
            )
            ExamResult.objects.update_or_create(
                student=student,
                exam=exam,
                defaults={"score": grade, "status": "قبول" if grade >= 10 else "مردود"},
            )

    for offer in current_offers:
        Transcript.objects.update_or_create(
            student=student,
            class_offer=offer,
            defaults={"final_grade": None, "pass_status": False},
        )
        exam, _ = Exam.objects.get_or_create(
            class_offer=offer,
            exam_type="میان‌ترم",
            exam_date=date.today() + timedelta(days=45),
            defaults={"exam_location": offer.class_group.class_location, "exam_duration": 90},
        )
        ExamResult.objects.update_or_create(
            student=student,
            exam=exam,
            defaults={"score": Decimal("17.50"), "status": "قبول"},
        )

    extra_offers = []
    for j, lesson in enumerate(lessons[7:12]):
        teacher = teachers[(j + 3) % len(teachers)]
        offer = _class_for(
            lesson, current_term, teacher, "پنج‌شنبه", f"C{200+j}", time(10, 0),
            f"1404-OPT{j+1}",
        )
        extra_offers.append(offer)

    payment_banks = ["ملت", "ملی", "صادرات", "پاسارگاد", "سامان", "آینده"]
    payment_amounts = [12_500_000, 8_000_000, 5_000_000, 3_500_000, 25_000_000, 6_000_000]
    for i in range(24):
        confirmed = i % 5 != 1
        StudentPayments.objects.update_or_create(
            tracking_code=f"DEMO-PAY-{i+1:04d}",
            defaults={
                "student": student,
                "amount": payment_amounts[i % len(payment_amounts)],
                "payment_datetime": now - timedelta(days=i * 12 + 3),
                "is_confirmed": confirmed,
                "reference_bank": payment_banks[i % len(payment_banks)],
            },
        )

    announcements = [
        ("شروع ثبت‌نام نیمسال جاری", "ثبت‌نام نیمسال اول ۱۴۰۴ از ۱ مهر آغاز می‌شود.", True),
        ("اعلام برنامه امتحانات", "برنامه امتحانات پایان‌ترم در سامانه منتشر شد.", True),
        ("کارگاه رزومه‌نویسی", "کارگاه آمادگی برای بازار کار — چهارشنبه ۱۴۰۴/۰۷/۲۰", False),
        ("تمدید مهلت حذف و اضافه", "مهلت حذف و اضافه تا پایان هفته تمدید شد.", True),
        ("اطلاعیه بورسیه", "ثبت‌نام بورسیه شایستگی تحصیلی برای دانشجویان ممتاز.", False),
        ("تعطیلات رسمی", "دانشگاه در روز ۲۲ بهمن تعطیل است.", False),
        ("کلاس‌های جبرانی", "برنامه کلاس‌های جبرانی هفته آینده اعلام شد.", False),
        ("سامانه آموزشیار", "نسخه جدید سامانه آموزشیار با امکانات بیشتر فعال شد.", True),
    ]
    for i, (title, body, urgent) in enumerate(announcements):
        AcademicAnnouncement.objects.get_or_create(
            title=title,
            defaults={
                "body": body,
                "announcement_type": cv_ann_type,
                "audience": cv_ann_audience,
                "status": cv_ann_status,
                "creator": admin_person,
                "is_urgent": urgent,
                "summary": title[:80],
                "department_code": dept.department_code,
            },
        )

    taken_units = sum(
        t.class_offer.class_group.lesson.units
        for t in Transcript.objects.filter(student=student, pass_status=True).select_related(
            "class_offer__class_group__lesson"
        )
    )
    passed = Transcript.objects.filter(student=student, pass_status=True, final_grade__isnull=False)
    if passed.exists():
        gpa = sum(t.final_grade for t in passed) / passed.count()
    else:
        gpa = Decimal("16.60")

    student.gpa = round(gpa, 2)
    student.current_term_gpa = Decimal("18.20")
    student.taken_units = taken_units or 78
    student.save(update_fields=["gpa", "current_term_gpa", "taken_units"])

    write(f"  Rich data: {len(current_offers)} current courses, {taken_units} units, GPA {student.gpa}")
    return ctx
