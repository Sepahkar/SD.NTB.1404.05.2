import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


# =============================================================================
# ConstValue
# =============================================================================
class ConstValue(models.Model):
    caption = models.CharField(max_length=200, verbose_name=_("عنوان"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("کد"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال بودن"))
    parent = models.ForeignKey("self",on_delete=models.CASCADE,null=True,blank=True,related_name="children",verbose_name=_("والد"),)
    name = models.CharField(max_length=100, blank=True, verbose_name=_("نام مقدار"))
    value = models.CharField(max_length=100, blank=True, verbose_name=_("مقدار"))
    value_title = models.CharField(max_length=100, blank=True, verbose_name=_("عنوان مقدار ثابت"))

    class Meta:
        db_table = "const_values"
        verbose_name = _("مقدار ثابت")
        verbose_name_plural = _("مقادیر ثابت")

    def __str__(self):
        return self.caption or self.value_title or self.name or self.value or str(self.pk)


# =============================================================================
# Person
# =============================================================================
class Person(models.Model):
    SECURITY_QUESTION_CHOICES = [
        ("mother_name", _("نام مادر")),
        ("first_school", _("نام اولین مدرسه")),
        ("birth_city", _("شهر تولد")),
        ("favorite_book", _("نام کتاب مورد علاقه")),
    ]
    GENDER_CHOICES = [
        ("male", _("مرد")),
        ("female", _("زن")),
        ("other", _("سایر")),
    ]

    username = models.CharField(max_length=150, unique=True, verbose_name=_("نام کاربری"))
    password = models.CharField(max_length=128, verbose_name=_("رمز عبور")) 
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("نام"))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_("نام خانوادگی"))
    full_name = models.CharField(max_length=200, blank=True, verbose_name=_("نام کامل"))
    national_code = models.CharField(max_length=10, unique=True, verbose_name=_("کد ملی"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال بودن"))
    is_online = models.BooleanField(default=False, verbose_name=_("وضعیت آنلاین"))
    preferred_language = models.CharField(max_length=10, default="fa", verbose_name=_("زبان انتخابی"))
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="other", verbose_name=_("جنسیت"))
    birth_date = models.DateField(null=True, blank=True, verbose_name=_("تاریخ تولد"))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_("کد پستی"))
    is_email_verified = models.BooleanField(default=False, verbose_name=_("تایید ایمیل"))
    place_of_birth = models.CharField(max_length=100, blank=True, verbose_name=_("محل تولد"))
    emergency_phone = models.CharField(max_length=20, blank=True, verbose_name=_("تلفن اضطراری"))
    is_foreign = models.BooleanField(default=False, verbose_name=_("اتباع خارجی"))
    failed_login = models.PositiveIntegerField(default=0, verbose_name=_("ورود ناموفق"))
    religion = models.CharField(max_length=50, blank=True, verbose_name=_("دین"))
    marital_status = models.CharField(max_length=20, default="مجرد", verbose_name=_("وضعیت تأهل"))
    security_question = models.CharField(max_length=255,choices=SECURITY_QUESTION_CHOICES,blank=True,verbose_name=_("سوال امنیتی"),)
    security_answer = models.CharField(max_length=255, blank=True, verbose_name=_("پاسخ امنیتی"))
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name=_("آخرین ورود"))
    account_locked = models.BooleanField(default=False, verbose_name=_("قفل حساب"))
    nationality = models.CharField(max_length=100, blank=True, verbose_name=_("ملیت"))

    class Meta:
        db_table = "persons"
        verbose_name = _("شخص")
        verbose_name_plural = _("اشخاص")

    def __str__(self):
        if self.full_name:
            return self.full_name
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def save(self, *args, **kwargs):
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)


# =============================================================================
# PhoneNumber / EmailAddress
# =============================================================================
class PhoneNumber(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="phone_numbers",
        verbose_name=_("شخص"),
    )
    phone = models.CharField(max_length=20, verbose_name=_("شماره تماس"))

    class Meta:
        db_table = "phone_numbers"
        verbose_name = _("شماره تلفن")
        verbose_name_plural = _("شماره‌های تلفن")

    def __str__(self):
        return self.phone


class EmailAddress(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="email_addresses",
        verbose_name=_("شخص"),
    )
    email = models.EmailField(verbose_name=_("ایمیل"))

    EMAIL_TYPE_CHOICES = [
        ("personal", _("شخصی")),
        ("work", _("کاری")),
        ("academic", _("تحصیلی")),
    ]
    email_type = models.CharField(
        max_length=20,
        choices=EMAIL_TYPE_CHOICES,
        default="personal",
        verbose_name=_("نوع ایمیل"),
    )
    is_primary = models.BooleanField(default=False, verbose_name=_("ایمیل اصلی"))
    verified = models.BooleanField(default=False, verbose_name=_("تایید شده"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))

    class Meta:
        db_table = "email_addresses"
        verbose_name = _("ایمیل")
        verbose_name_plural = _("ایمیل‌ها")

    def __str__(self):
        return self.email


# =============================================================================
# Department
# =============================================================================
class Department(models.Model):
    department_code = models.CharField(max_length=20, primary_key=True, verbose_name=_("کد دانشکده"))
    department_title = models.CharField(max_length=200, verbose_name=_("عنوان دانشکده"))
    dean_name = models.CharField(max_length=100, blank=True, verbose_name=_("رئیس دانشکده"))
    establish_year = models.DateField(null=True, blank=True, verbose_name=_("سال تأسیس"))
    student_count = models.IntegerField(default=0, verbose_name=_("تعداد دانشجویان"))
    department_address = models.TextField(blank=True, verbose_name=_("آدرس دانشکده"))
    website_url = models.URLField(blank=True, verbose_name=_("وب‌سایت"))
    phone_number = models.CharField(max_length=20, blank=True, verbose_name=_("تلفن"))
    name = models.CharField(max_length=100, blank=True, verbose_name=_("نام گروه آموزشی"))


    class Meta:
        db_table = "departments"
        verbose_name = _("دانشکده")
        verbose_name_plural = _("دانشکده‌ها")

    def __str__(self):
        return self.department_title or self.name or self.department_code


# =============================================================================
# EducationBranch / Tendency / Term
# =============================================================================
class EducationBranch(models.Model):
    DEGREE_LEVELS = [
        ("diploma", _("دیپلم")),
        ("associate", _("کاردانی")),
        ("bachelor", _("کارشناسی")),
        ("master", _("کارشناسی ارشد")),
        ("doctorate", _("دکتری")),
    ]
    title = models.CharField(max_length=200, verbose_name=_("نام رشته"))
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="branches",
        verbose_name=_("دانشکده"),
    )
    degree_level = models.CharField(max_length=50, choices=DEGREE_LEVELS, verbose_name=_("مقطع"))

    class Meta:
        verbose_name = _("رشته تحصیلی")
        verbose_name_plural = _("رشته‌های تحصیلی")

    def __str__(self):
        return f"{self.title} ({self.get_degree_level_display()})"


class Tendency(models.Model):
    tendency_code = models.IntegerField(primary_key=True, verbose_name=_("کد گرایش"))
    tendency_name = models.CharField(max_length=200, verbose_name=_("نام گرایش"))
    field = models.ForeignKey(to=EducationBranch, on_delete=models.CASCADE,null=True, blank=True, verbose_name=_("کد رشته"))
    total_units = models.IntegerField(default=0, verbose_name=_("کل واحد"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))

    class Meta:
        db_table = "tendency"
        verbose_name = _("گرایش")
        verbose_name_plural = _("گرایش‌ها")

    def __str__(self):
        return self.tendency_name


class Term(models.Model):
    term_id = models.IntegerField(primary_key=True, verbose_name=_("شناسه ترم"))
    term_title = models.CharField(max_length=200, verbose_name=_("عنوان ترم"))
    start_term = models.DateField(verbose_name=_("شروع"))
    end_term = models.DateField(verbose_name=_("پایان"))
    is_current = models.BooleanField(default=False, verbose_name=_("ترم جاری"))
    registration_start = models.DateTimeField(verbose_name=_("شروع ثبت‌نام"))

    name = models.CharField(max_length=100, blank=True, verbose_name=_("نام ترم"))

    class Meta:
        db_table = "term"
        verbose_name = _("ترم")
        verbose_name_plural = _("ترم‌ها")

    def __str__(self):
        return self.term_title or self.name


# =============================================================================
# Teacher
# =============================================================================
class Teacher(models.Model):
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        null=True,
        blank=True,
        verbose_name=_("شخص"),
    )
    full_name = models.CharField(max_length=100, blank=True, verbose_name=_("نام کامل"))


    class Meta:
        verbose_name = _("استاد")
        verbose_name_plural = _("اساتید")

    def __str__(self):
        return self.full_name or str(self.person or self.pk)


class TeacherResearchInterest(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="research_interests",
        verbose_name=_("استاد"),
    )
    research_interest = models.TextField(blank=True, verbose_name=_("حوزه تحقیقاتی"))

    class Meta:
        verbose_name = _("علاقه‌مندی پژوهشی")
        verbose_name_plural = _("علاقه‌مندی‌های پژوهشی")

    def __str__(self):
        return (self.research_interest or "")[:50]


# =============================================================================
# Student
# =============================================================================
class Student(models.Model):
    MILITARY_STATUS = [
        ("exempt", _("معاف")),
        ("served", _("پایان خدمت")),
        ("pending", _("مشمول")),
        ("studying", _("معافیت تحصیلی")),
    ]
    PAYMENT_TYPE_CHOICES = [
        ("end_of_term", _("پایان ترم")),
        ("installment", _("اقساطی")),
    ]

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="student_profile",
        null=True,
        blank=True,
        verbose_name=_("شخص"),
    )

    student_number = models.CharField(max_length=20, unique=True, verbose_name=_("شماره دانشجویی"))
    entry_year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("سال ورود"))
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="students",
        verbose_name=_("دانشکده"),
    )
    branch = models.ForeignKey(
        EducationBranch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name=_("رشته"),
    )
    tendency = models.ForeignKey(
        Tendency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name=_("گرایش"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    enrollment_date = models.DateField(auto_now_add=True, verbose_name=_("تاریخ ثبت‌نام"))
    military_status = models.CharField(
        max_length=20,
        choices=MILITARY_STATUS,
        blank=True,
        verbose_name=_("وضعیت سربازی"),
    )
    education_branch = models.ForeignKey(
        EducationBranch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrolled_students",
        verbose_name=_("رشته (گودرزی)"),
    )
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name=_("معدل"))

    academic_warning_count = models.IntegerField(default=0, verbose_name=_("تعداد هشدار آموزشی"))
    expected_graduation_date = models.DateField(null=True, blank=True, verbose_name=_("تاریخ فارغ‌التحصیلی پیش‌بینی"))
    educational_email = models.EmailField(blank=True, verbose_name=_("ایمیل آموزشی"))
    gpa_rank = models.IntegerField(null=True, blank=True, verbose_name=_("رتبه معدل"))
    advisor_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advised_students",
        verbose_name=_("استاد راهنما"),
    )
    payment_type = models.CharField(
        max_length=50,
        choices=PAYMENT_TYPE_CHOICES,
        default="end_of_term",
        verbose_name=_("نوع پرداخت"),
    )

    emergency_contact_name = models.CharField(max_length=100, blank=True, verbose_name=_("نام تماس اضطراری"))
    emergency_contact_relation = models.CharField(max_length=100, blank=True, verbose_name=_("نسبت تماس اضطراری"))
    blood_type = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students_by_blood_type",
        verbose_name=_("گروه خونی"),
    )
    dormitory_status = models.BooleanField(default=False, verbose_name=_("وضعیت خوابگاه"))
    graduation_status = models.BooleanField(default=False, verbose_name=_("فارغ‌التحصیل"))
    current_term_gpa = models.FloatField(default=0, verbose_name=_("معدل ترم جاری"))
    taken_units = models.IntegerField(default=0, verbose_name=_("واحد اخذ شده"))
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("نام (کتابخانه)"))
    last_name = models.CharField(max_length=150, blank=True, verbose_name=_("نام خانوادگی (کتابخانه)"))

    class Meta:
        db_table = "students"
        verbose_name = _("دانشجو")
        verbose_name_plural = _("دانشجویان")
        ordering = ["student_number"]

    def __str__(self):
        if self.person_id:
            return f"{self.student_number} - {self.person}"
        return f"{self.student_number} - {self.first_name} {self.last_name}".strip()


# =============================================================================
# Employee
# =============================================================================
class Employee(models.Model):
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        null=True,
        blank=True,
        verbose_name=_("شخص"),
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name=_("دانشکده"),
    )
    position = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees_by_position",
        verbose_name=_("سمت"),
    )
    hire_date = models.DateField(null=True, blank=True, verbose_name=_("تاریخ استخدام"))
    salary = models.IntegerField(default=0, verbose_name=_("حقوق پایه"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    employee_code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name=_("کد پرسنلی"))
    office_room_number = models.CharField(max_length=20, blank=True, verbose_name=_("شماره اتاق"))
    bank_account_number = models.CharField(max_length=30, blank=True, verbose_name=_("شماره حساب"))
    insurance_number = models.CharField(max_length=50, blank=True, verbose_name=_("شماره بیمه"))
    supervisor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
        verbose_name=_("سرپرست"),
    )
    work_shift = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees_by_shift",
        verbose_name=_("شیفت کاری"),
    )
    employment_type = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees_by_employment_type",
        verbose_name=_("نوع استخدام"),
    )
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_("اضافه‌کاری"))

    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("نام (کتابخانه)"))
    last_name = models.CharField(max_length=150, blank=True, verbose_name=_("نام خانوادگی (کتابخانه)"))
    personnel_code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name=_("کد پرسنلی (کتابخانه)"))

    class Meta:
        db_table = "employees"
        verbose_name = _("کارمند")
        verbose_name_plural = _("کارمندان")

    def __str__(self):
        return f"{self.employee_code or self.personnel_code} - {self.person}"


# =============================================================================
# Lesson / Class / ClassOffer
# =============================================================================
class Lesson(models.Model):
    lesson_code = models.CharField(max_length=20, unique=True, verbose_name=_("کد درس"))
    title = models.CharField(max_length=200, verbose_name=_("عنوان درس"))
    units = models.PositiveSmallIntegerField(default=0, verbose_name=_("واحد"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("دانشکده"),
    )

    education_branch = models.ForeignKey(
        EducationBranch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
        verbose_name=_("رشته"),
    )
    prerequisites = models.ManyToManyField("self", symmetrical=False, blank=True, verbose_name=_("پیش‌نیازها"))

    practical_units = models.IntegerField(default=0, verbose_name=_("واحد عملی"))
    theoretical_units = models.IntegerField(default=0, verbose_name=_("واحد نظری"))
    syllabus_file = models.FileField(upload_to="syllabus/", null=True, blank=True, verbose_name=_("سیلابس"))

    lesson_language = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons_by_language",
        verbose_name=_("زبان تدریس"),
    )
    lesson_hours = models.IntegerField(default=48, verbose_name=_("ساعات درس"))

    lesson_type = models.CharField(max_length=50, default="تخصصی", verbose_name=_("نوع درس"))
    minimum_score = models.FloatField(default=10, verbose_name=_("حداقل نمره قبولی"))


    class Meta:
        db_table = "lessons"
        verbose_name = _("درس")
        verbose_name_plural = _("دروس")

    def __str__(self):
        return f"{self.lesson_code} - {self.title}"


class Class(models.Model):
    """کلاس / گروه درسی — نام Class به‌دلیل کلمهٔ رزرو پایتون در Meta db_table نگه داشته شده."""

    class_id = models.AutoField(primary_key=True, verbose_name=_("شناسه کلاس"))
    class_number = models.CharField(max_length=50, verbose_name=_("شماره کلاس"))
    max_capacity = models.IntegerField(default=30, verbose_name=_("ظرفیت"))
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="classes", verbose_name=_("ترم"))
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name="classes", verbose_name=_("درس"))
    class_time = models.TimeField(null=True, blank=True, verbose_name=_("ساعت کلاس"))
    tendency = models.ForeignKey(
        Tendency,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="classes",
        verbose_name=_("گرایش"),
    )

    recorded_sessions_available = models.BooleanField(default=False, verbose_name=_("جلسات ضبط‌شده"))
    attendance_mandatory = models.BooleanField(default=True, verbose_name=_("حضور اجباری"))

    max_absence_limit = models.IntegerField(default=3, verbose_name=_("حد مجاز غیبت"))
    class_location = models.CharField(max_length=100, blank=True, verbose_name=_("محل کلاس"))
    class_type = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes_by_type",
        verbose_name=_("نوع کلاس"),
    )

    class_day = models.CharField(max_length=50, default="شنبه", verbose_name=_("روز برگزاری"))

    class Meta:
        db_table = "class"
        verbose_name = _("کلاس")
        verbose_name_plural = _("کلاس‌ها")

    def __str__(self):
        return f"کلاس {self.class_number}"


class ClassOffer(models.Model):
    """ارائهٔ درس — برای کارنامه و آزمون (حمیدرضا شیدایی)."""
    class_group = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="offers", verbose_name=_("کلاس"))
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("استاد"))
    term = models.ForeignKey(Term, on_delete=models.PROTECT, verbose_name=_("ترم"))

    class Meta:
        verbose_name = _("ارائه درس")
        verbose_name_plural = _("ارائه‌های درس")

    def __str__(self):
        return f"{self.class_group} - {self.term}"


# =============================================================================
# Exam / Attendance / Transcript
# =============================================================================
class Exam(models.Model):
    exam_type = models.CharField(max_length=50, verbose_name=_("نوع آزمون"))
    exam_date = models.DateField(verbose_name=_("تاریخ آزمون"))
    class_offer = models.ForeignKey(
        ClassOffer,
        on_delete=models.CASCADE,
        related_name="exams",
        verbose_name=_("ارائه درس"),
    )

    correction_deadline = models.DateField(null=True, blank=True, verbose_name=_("مهلت تصحیح"))

    exam_location = models.CharField(max_length=100, blank=True, verbose_name=_("محل برگزاری"))

    exam_duration = models.IntegerField(default=90, verbose_name=_("مدت (دقیقه)"))

    class Meta:
        db_table = "exam"
        verbose_name = _("آزمون")
        verbose_name_plural = _("آزمون‌ها")

    def __str__(self):
        return f"{self.exam_type} - {self.exam_date}"


class ExamInvigilator(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="invigilators", verbose_name=_("آزمون"))
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="invigilation_duties", verbose_name=_("مراقب"))

    class Meta:
        verbose_name = _("مراقب آزمون")
        verbose_name_plural = _("مراقبان آزمون")

    def __str__(self):
        return f"{self.exam_id} - {self.employee_id}"


class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="exam_results", verbose_name=_("دانشجو"))
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results", verbose_name=_("آزمون"))
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("نمره"))
    status = models.CharField(max_length=20, verbose_name=_("وضعیت"))

    def __str__(self):
        return f"{self.student} - {self.score}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances", verbose_name=_("دانشجو"))
    class_offer = models.ForeignKey(
        ClassOffer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attendances",
        verbose_name=_("ارائه درس"),
    )
    attendance_status = models.CharField(max_length=20, verbose_name=_("وضعیت حضور"))
    session_number = models.IntegerField(verbose_name=_("شماره جلسه"))

    absence_description = models.TextField(blank=True, verbose_name=_("توضیح غیبت"))

    class Meta:
        verbose_name = _("حضور و غیاب")
        verbose_name_plural = _("حضور و غیاب‌ها")

    def __str__(self):
        return f"{self.student} - جلسه {self.session_number}"


class Transcript(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="transcripts", verbose_name=_("دانشجو"))
    class_offer = models.ForeignKey(ClassOffer, on_delete=models.CASCADE, related_name="transcripts", verbose_name=_("ارائه درس"))
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("نمره نهایی"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخرین بروزرسانی"))
    pass_status = models.BooleanField(default=False, verbose_name=_("قبول"))

    class Meta:
        verbose_name = _("کارنامه")
        verbose_name_plural = _("کارنامه‌ها")

    def __str__(self):
        return f"{self.student} - {self.final_grade}"


# =============================================================================
# Payments
# =============================================================================
class StudentPayments(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payments", verbose_name=_("دانشجو"))
    amount = models.IntegerField(default=0, verbose_name=_("مبلغ"))
    payment_datetime = models.DateTimeField(verbose_name=_("زمان پرداخت"))
    is_confirmed = models.BooleanField(default=False, verbose_name=_("تایید شده"))
    tracking_code = models.CharField(max_length=12, verbose_name=_("کد پیگیری"))
    reference_bank = models.CharField(max_length=20, verbose_name=_("بانک مرجع"))

    payment_method = models.CharField(max_length=50, default="آنلاین", verbose_name=_("روش پرداخت"))

    installment_count = models.IntegerField(default=1, verbose_name=_("تعداد قسط"))

    class Meta:
        db_table = "student_payments"
        verbose_name = _("پرداخت دانشجو")
        verbose_name_plural = _("پرداخت‌های دانشجو")

    def __str__(self):
        return f"پرداخت {self.amount} - {self.student_id}"


# =============================================================================
# StudentRequest / AcademicLeave
# =============================================================================
class StudentRequest(models.Model):
    request_date = models.DateField(verbose_name=_("تاریخ درخواست"))
    request_type = models.ForeignKey(
        ConstValue,
        on_delete=models.PROTECT,
        related_name="requests_by_type",
        verbose_name=_("نوع درخواست"),
    )
    description = models.TextField(verbose_name=_("شرح"))
    status = models.ForeignKey(
        ConstValue,
        on_delete=models.PROTECT,
        related_name="requests_by_status",
        verbose_name=_("وضعیت"),
    )
    employee_follower = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="followed_requests",
        verbose_name=_("کارمند پیگیر"),
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="requests",
        verbose_name=_("دانشجو"),
    )

    response_text = models.TextField(blank=True, verbose_name=_("متن پاسخ"))
    responder_person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="given_responses",
        verbose_name=_("پاسخ‌دهنده"),
    )

    class Meta:
        db_table = "student_requests"
        verbose_name = _("درخواست دانشجو")
        verbose_name_plural = _("درخواست‌های دانشجو")

    def __str__(self):
        return f"درخواست {self.pk}"


class AcademicLeaveRequest(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="leave_requests",
        verbose_name=_("دانشجو"),
    )
    request_date = models.DateField(auto_now_add=True, verbose_name=_("تاریخ درخواست"))
    leave_reason = models.TextField(verbose_name=_("دلیل مرخصی"))
    is_approved = models.BooleanField(default=False, verbose_name=_("تایید شده"))

    class Meta:
        db_table = "academic_leave_request"
        verbose_name = _("درخواست مرخصی تحصیلی")
        verbose_name_plural = _("درخواست‌های مرخصی")

    def __str__(self):
        return f"مرخصی {self.pk} - {self.request_date}"


# =============================================================================
# Skills / Address
# =============================================================================
class PersonSkill(models.Model):
    SKILL_LEVELS = [
        ("beginner", _("مبتدی")),
        ("intermediate", _("متوسط")),
        ("advanced", _("پیشرفته")),
    ]
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="skills", verbose_name=_("شخص"))
    name = models.CharField(max_length=100, verbose_name=_("مهارت"))
    level = models.CharField(max_length=20, choices=SKILL_LEVELS, verbose_name=_("سطح"))

    class Meta:
        verbose_name = _("مهارت")
        verbose_name_plural = _("مهارت‌ها")

    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"


class PostalAddress(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="addresses", verbose_name=_("شخص"))
    address_detail = models.TextField(verbose_name=_("آدرس"))
    city = models.CharField(max_length=100, blank=True, verbose_name=_("شهر"))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_("کد پستی"))

    class Meta:
        verbose_name = _("آدرس پستی")
        verbose_name_plural = _("آدرس‌های پستی")

    def __str__(self):
        return self.address_detail[:50]


# =============================================================================
# Library / Books
# =============================================================================
class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("عنوان"))
    isbn = models.CharField(max_length=20, blank=True, verbose_name=_("شابک"))

    class Meta:
        verbose_name = _("کتاب")
        verbose_name_plural = _("کتاب‌ها")

    def __str__(self):
        return self.title


class LibraryBookLending(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="lendings", verbose_name=_("کتاب"))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="book_lendings", verbose_name=_("دانشجو"))
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name="processed_lendings",
        verbose_name=_("کتابدار"),
    )
    status = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        related_name="lendings_by_status",
        verbose_name=_("وضعیت"),
    )
    loan_date = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ امانت"))
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("سررسید"))
    return_date = models.DateTimeField(null=True, blank=True, verbose_name=_("بازگشت"))
    is_returned = models.BooleanField(default=False, verbose_name=_("برگشت داده شده"))
    renewal_count = models.IntegerField(default=0, verbose_name=_("تمدید"))
    fine_amount = models.IntegerField(default=0, verbose_name=_("جریمه"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("امانت کتاب")
        verbose_name_plural = _("امانت‌های کتاب")

    def __str__(self):
        return f"{self.book} → {self.student}"


class LibraryResource(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="library_reserves", verbose_name=_("کاربر"))
    resource_name = models.CharField(max_length=255, verbose_name=_("نام منبع"))
    reserve_date = models.DateField(auto_now_add=True, verbose_name=_("تاریخ رزرو"))
    is_returned = models.BooleanField(default=False, verbose_name=_("عودت"))

    lost_status = models.BooleanField(default=False, verbose_name=_("مفقود"))

    class Meta:
        verbose_name = _("رزرو کتابخانه")
        verbose_name_plural = _("رزروهای کتابخانه")

    def __str__(self):
        return self.resource_name


# =============================================================================
# Scholarship / Dormitory / Loan
# =============================================================================
class Scholarship(models.Model):
    STATUS_CHOICES = [
        ("pending", _("در انتظار")),
        ("approved", _("تایید شده")),
        ("rejected", _("رد شده")),
    ]
    title = models.CharField(max_length=255, verbose_name=_("عنوان بورسیه"))
    amount = models.IntegerField(verbose_name=_("مبلغ"))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="scholarships", verbose_name=_("دانشجو"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name=_("وضعیت"))

    def __str__(self):
        return self.title


class DormitoryRequest(models.Model):
    APPROVAL_CHOICES = [
        ("pending", _("در انتظار")),
        ("approved", _("تایید شده")),
        ("rejected", _("رد شده")),
    ]
    ROOM_TYPE_CHOICES = [
        ("2_person", _("دو نفره")),
        ("4_person", _("چهار نفره")),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="dormitory_requests", verbose_name=_("دانشجو"))
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, verbose_name=_("نوع اتاق"))
    request_date = models.DateField(auto_now_add=True, verbose_name=_("تاریخ درخواست"))
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default="pending", verbose_name=_("وضعیت"))

    def __str__(self):
        return f"{self.student} - {self.room_type}"


class Loan(models.Model):
    LOAN_STATUS_CHOICES = [
        ("active", _("فعال")),
        ("closed", _("بسته")),
        ("pending", _("در انتظار")),
    ]
    PERSON_TYPE_CHOICES = [
        ("person", _("شخص")),
        ("consultative", _("مشاوره‌ای")),
    ]
    borrower = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name=_("دریافت‌کننده"),
    )
    amount = models.BigIntegerField(default=0, verbose_name=_("مبلغ وام"))
    loan_status = models.CharField(max_length=50, choices=LOAN_STATUS_CHOICES, verbose_name=_("وضعیت"))
    document_file = models.FileField(upload_to="loan_documents/", null=True, blank=True, verbose_name=_("فایل درخواست"))
    loan_payment_date = models.CharField(max_length=100, blank=True, verbose_name=_("تاریخ پرداخت"))
    loan_request_date = models.DateTimeField(verbose_name=_("تاریخ درخواست"))
    loan_type = models.CharField(max_length=100, verbose_name=_("نوع وام"))
    amount_of_each_loan_installment = models.BigIntegerField(verbose_name=_("مبلغ هر قسط"))
    loan_repayment_period = models.IntegerField(verbose_name=_("دوره بازپرداخت"))
    loan_installment_date = models.DateField(verbose_name=_("تاریخ اولین قسط"))
    number_of_loan_installments = models.IntegerField(verbose_name=_("تعداد اقساط"))
    loan_request_conditions = models.TextField(blank=True, verbose_name=_("شرایط"))
    how_to_pay_loan_installments = models.CharField(max_length=255, verbose_name=_("نحوه پرداخت اقساط"))
    loan_file_number = models.CharField(max_length=100, unique=True, verbose_name=_("شماره پرونده"))
    personal_type = models.CharField(
        max_length=50,
        choices=PERSON_TYPE_CHOICES,
        default="person",
        verbose_name=_("نوع شخصیت"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("وام")
        verbose_name_plural = _("وام‌ها")

    def __str__(self):
        return f"{self.loan_file_number} - {self.amount}"


# =============================================================================
# Internship / Documents / AcademicProgram
# =============================================================================
class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("نام شرکت"))
    registration_number = models.CharField(max_length=50, blank=True, verbose_name=_("شناسه ثبت"))

    def __str__(self):
        return self.name


class Internship(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="internships", verbose_name=_("دانشجو"))
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="internships", verbose_name=_("شرکت"))
    start_date = models.DateField(verbose_name=_("شروع"))
    finish_date = models.DateField(verbose_name=_("پایان"))
    evaluation_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_("نمره ارزیابی"))

    class Meta:
        verbose_name = _("کارآموزی")
        verbose_name_plural = _("کارآموزی‌ها")


class DocumentStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents", verbose_name=_("دانشجو"))
    document_type = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        related_name="student_doc_types",
        verbose_name=_("نوع مدرک"),
    )
    upload_timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("زمان بارگذاری"))
    verification_status = models.ForeignKey(
        ConstValue,
        on_delete=models.SET_NULL,
        null=True,
        related_name="student_doc_verifications",
        verbose_name=_("وضعیت تایید"),
    )

    class Meta:
        verbose_name = _("مدرک دانشجو")
        verbose_name_plural = _("مدارک دانشجو")


class AcademicProgram(models.Model):
    program_title = models.CharField(max_length=255, verbose_name=_("عنوان برنامه"))
    degree_level = models.CharField(max_length=100, verbose_name=_("مقطع"))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programs", verbose_name=_("گروه"))
    start_programtime = models.DateField(verbose_name=_("شروع دوره"))
    finish_programtime = models.DateField(verbose_name=_("پایان دوره"))

    class Meta:
        verbose_name = _("برنامه آموزشی")
        verbose_name_plural = _("برنامه‌های آموزشی")


# =============================================================================
# AcademicEvent / AcademicAnnouncement
# =============================================================================
class AcademicEvent(models.Model):
    title_fa = models.CharField(max_length=255, default="بدون عنوان", verbose_name=_("عنوان فارسی"))
    title_en = models.CharField(max_length=255, blank=True, verbose_name=_("عنوان انگلیسی"))
    event_type = models.ForeignKey(
        ConstValue,
        on_delete=models.PROTECT,
        related_name="academic_events_by_type",
        verbose_name=_("نوع رویداد"),
    )
    start_date = models.DateField(verbose_name=_("شروع"))
    end_date = models.DateField(verbose_name=_("پایان"))
    location = models.CharField(max_length=255, blank=True, verbose_name=_("مکان"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    organizer_person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="organized_events",
        verbose_name=_("برگزارکننده"),
    )
    host_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hosted_events",
        verbose_name=_("دانشکده میزبان"),
    )
    status = models.ForeignKey(
        ConstValue,
        on_delete=models.PROTECT,
        related_name="academic_events_by_status",
        verbose_name=_("وضعیت"),
    )
    max_attendees = models.PositiveIntegerField(null=True, blank=True, default=100, verbose_name=_("حداکثر شرکت‌کننده"))
    registration_required = models.BooleanField(default=False, verbose_name=_("نیاز به ثبت‌نام"))
    registration_deadline = models.DateField(null=True, blank=True, verbose_name=_("مهلت ثبت‌نام"))
    contact_email = models.EmailField(blank=True, verbose_name=_("ایمیل تماس"))
    is_public = models.BooleanField(default=True, verbose_name=_("عمومی"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_event"
        verbose_name = _("رویداد آموزشی")
        verbose_name_plural = _("رویدادهای آموزشی")

    def __str__(self):
        return self.title_fa


class AcademicAnnouncement(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("عنوان"))
    body = models.TextField(verbose_name=_("متن"))
    announcement_type = models.ForeignKey(
        ConstValue,
        on_delete=models.PROTECT,
        related_name="announcements_by_type",
        verbose_name=_("نوع"),
    )
    audience = models.ForeignKey(
        ConstValue,
        on_delete=models.PROTECT,
        related_name="announcements_by_audience",
        verbose_name=_("مخاطب"),
    )
    department_code = models.CharField(max_length=20, blank=True, verbose_name=_("کد دانشکده"))
    publish_date = models.DateTimeField(auto_now_add=True, verbose_name=_("انتشار"))
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name=_("انقضا"))
    is_urgent = models.BooleanField(default=False, verbose_name=_("فوری"))
    summary = models.CharField(max_length=500, blank=True, verbose_name=_("خلاصه"))
    status = models.ForeignKey(
        ConstValue,
        on_delete=models.PROTECT,
        related_name="announcements_by_status",
        verbose_name=_("وضعیت"),
    )
    priority = models.IntegerField(default=3, verbose_name=_("اولویت"))
    view_count = models.IntegerField(default=0, verbose_name=_("بازدید"))
    allow_comment = models.BooleanField(default=True, verbose_name=_("امکان نظر"))
    creator = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="announcements_created",
        verbose_name=_("ثبت‌کننده"),
    )
    contact_email = models.EmailField(blank=True, verbose_name=_("ایمیل تماس"))

    class Meta:
        db_table = "academic_announcement"
        verbose_name = _("اطلاعیه آموزشی")
        verbose_name_plural = _("اطلاعیه‌های آموزشی")

    def __str__(self):
        return self.title


# =============================================================================
# TeacherEvaluation / PrerequisiteWarning
# =============================================================================
class TeacherEvaluation(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="evaluations", verbose_name=_("استاد"))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="teacher_evaluations", verbose_name=_("دانشجو"))
    term = models.ForeignKey(Term, on_delete=models.CASCADE, verbose_name=_("ترم"))
    teaching_quality = models.PositiveSmallIntegerField(default=3, verbose_name=_("کیفیت تدریس"))
    comment = models.TextField(blank=True, default="", verbose_name=_("نظر"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("زمان ثبت"))

    class Meta:
        verbose_name = _("ارزیابی استاد")
        verbose_name_plural = _("ارزیابی‌های استاد")

    def __str__(self):
        return f"{self.teacher} - {self.term}"


class PrerequisiteWarning(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="prerequisite_warnings", verbose_name=_("دانشجو"))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="prerequisite_warnings", verbose_name=_("درس"))
    prerequisite_avg = models.FloatField(verbose_name=_("میانگین پیش‌نیاز"))
    min_pass_threshold = models.FloatField(default=12.0, verbose_name=_("آستانه قبولی"))
    warning_date = models.DateField(auto_now_add=True, verbose_name=_("تاریخ هشدار"))
    is_ignored = models.BooleanField(default=False, verbose_name=_("نادیده گرفته شده"))
    approved_by_advisor = models.BooleanField(null=True, blank=True, verbose_name=_("تأیید مشاور"))
    advisor_note = models.TextField(blank=True, verbose_name=_("یادداشت مشاور"))
    student_action = models.CharField(max_length=200, blank=True, verbose_name=_("اقدام دانشجو"))
    term = models.ForeignKey(Term, on_delete=models.CASCADE, verbose_name=_("ترم"))
    created_by = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="created_warnings", verbose_name=_("ایجادکننده"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    class Meta:
        db_table = "prerequisite_warning"
        verbose_name = _("هشدار پیش‌نیاز")
        verbose_name_plural = _("هشدارهای پیش‌نیاز")

    def __str__(self):
        return f"هشدار {self.student_id} - {self.lesson_id}"


# =============================================================================
# Authentication (SIAVASH)
# =============================================================================
class AuthRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, unique=True, verbose_name=_("کد نقش"))
    name = models.CharField(max_length=150, verbose_name=_("نام نقش"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    class Meta:
        db_table = "auth_role"
        verbose_name = _("نقش")
        verbose_name_plural = _("نقش‌ها")

    def __str__(self):
        return self.name


class AuthAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="auth_account", verbose_name=_("شخص"))
    username = models.CharField(max_length=150, unique=True, verbose_name=_("نام کاربری"))
    email = models.EmailField(unique=True, verbose_name=_("ایمیل"))
    password_hash = models.CharField(max_length=255, verbose_name=_("هش رمز"))
    roles = models.ManyToManyField(AuthRole, through="AuthAccountRole", related_name="accounts", verbose_name=_("نقش‌ها"))

    class Meta:
        db_table = "auth_account"
        verbose_name = _("حساب احراز هویت")
        verbose_name_plural = _("حساب‌های احراز هویت")

    def __str__(self):
        return self.username


class AuthSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(AuthAccount, on_delete=models.CASCADE, related_name="sessions", verbose_name=_("حساب"))
    session_key = models.CharField(max_length=128, unique=True, verbose_name=_("کلید نشست"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP"))
    expires_at = models.DateTimeField(verbose_name=_("انقضا"))

    class Meta:
        db_table = "auth_session"
        verbose_name = _("نشست")
        verbose_name_plural = _("نشست‌ها")

    def __str__(self):
        return f"{self.account.username} - {self.session_key[:8]}"


class AuthAccountRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(AuthAccount, on_delete=models.CASCADE, related_name="account_role_links")
    role = models.ForeignKey(AuthRole, on_delete=models.CASCADE, related_name="role_account_links")
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_roles",
        verbose_name=_("تخصیص‌دهنده"),
    )

    class Meta:
        db_table = "auth_account_role"
        constraints = [
            models.UniqueConstraint(fields=["account", "role"], name="uq_auth_account_role"),
        ]

    def __str__(self):
        return f"{self.account.username} -> {self.role.code}"
