"""سریالایزرهای موجودیت‌های آموزشی."""

from rest_framework import serializers

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


class LessonSerializer(serializers.ModelSerializer):
    """درس / واحد درسی."""

    department_title = serializers.CharField(source="department.department_title", read_only=True)
    prerequisites = serializers.PrimaryKeyRelatedField(many=True, queryset=Lesson.objects.all(), required=False)

    class Meta:
        model = Lesson
        fields = "__all__"


class ClassSerializer(serializers.ModelSerializer):
    """گروه درسی."""

    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    term_title = serializers.CharField(source="term.term_title", read_only=True)

    class Meta:
        model = Class
        fields = "__all__"


class ClassOfferSerializer(serializers.ModelSerializer):
    """ارائه کلاس در نیمسال (استاد + زمان)."""

    lesson_title = serializers.CharField(source="class_group.lesson.title", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True, allow_null=True)
    class_number = serializers.CharField(source="class_group.class_number", read_only=True)

    class Meta:
        model = ClassOffer
        fields = "__all__"


class ExamSerializer(serializers.ModelSerializer):
    """امتحان."""

    class Meta:
        model = Exam
        fields = "__all__"


class ExamInvigilatorSerializer(serializers.ModelSerializer):
    """مراقب امتحان."""

    class Meta:
        model = ExamInvigilator
        fields = "__all__"


class ExamResultSerializer(serializers.ModelSerializer):
    """نتیجه امتحان دانشجو."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)
    exam_type = serializers.CharField(source="exam.exam_type", read_only=True)

    class Meta:
        model = ExamResult
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    """حضور و غیاب دانشجو."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)

    class Meta:
        model = Attendance
        fields = "__all__"


class TranscriptSerializer(serializers.ModelSerializer):
    """رکورد کارنامه (نمره نهایی درس)."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)
    lesson_title = serializers.CharField(source="class_offer.class_group.lesson.title", read_only=True)
    lesson_code = serializers.CharField(source="class_offer.class_group.lesson.lesson_code", read_only=True)
    term_title = serializers.CharField(source="class_offer.term.term_title", read_only=True)

    class Meta:
        model = Transcript
        fields = "__all__"


class TeacherEvaluationSerializer(serializers.ModelSerializer):
    """ارزیابی استاد توسط دانشجو."""

    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    student_number = serializers.CharField(source="student.student_number", read_only=True)

    class Meta:
        model = TeacherEvaluation
        fields = "__all__"


class PrerequisiteWarningSerializer(serializers.ModelSerializer):
    """هشدار نقض پیش‌نیاز."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = PrerequisiteWarning
        fields = "__all__"
