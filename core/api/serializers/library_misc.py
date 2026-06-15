"""سریالایزرهای کتابخانه، رویدادها و موجودیت‌های متفرقه."""

from rest_framework import serializers

from core.models import (
    AcademicAnnouncement,
    AcademicEvent,
    AcademicProgram,
    Book,
    Company,
    DocumentStudent,
    Internship,
    LibraryBookLending,
    LibraryResource,
)


class BookSerializer(serializers.ModelSerializer):
    """کتاب."""

    class Meta:
        model = Book
        fields = "__all__"


class LibraryBookLendingSerializer(serializers.ModelSerializer):
    """امانت کتاب از کتابخانه."""

    book_title = serializers.CharField(source="book.title", read_only=True)
    student_number = serializers.CharField(source="student.student_number", read_only=True)

    class Meta:
        model = LibraryBookLending
        fields = "__all__"


class LibraryReserveSerializer(serializers.ModelSerializer):
    """رزرو منبع کتابخانه — مدل LibraryResource."""

    person_name = serializers.CharField(source="person.full_name", read_only=True)

    class Meta:
        model = LibraryResource
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    """شرکت (کارآموزی)."""

    class Meta:
        model = Company
        fields = "__all__"


class InternshipSerializer(serializers.ModelSerializer):
    """کارآموزی دانشجو."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Internship
        fields = "__all__"


class DocumentStudentSerializer(serializers.ModelSerializer):
    """مدرک / سند دانشجو."""

    student_number = serializers.CharField(source="student.student_number", read_only=True)

    class Meta:
        model = DocumentStudent
        fields = "__all__"


class AcademicProgramSerializer(serializers.ModelSerializer):
    """برنامه آموزشی."""

    department_title = serializers.CharField(source="department.department_title", read_only=True)

    class Meta:
        model = AcademicProgram
        fields = "__all__"


class AcademicEventSerializer(serializers.ModelSerializer):
    """رویداد آموزشی."""

    class Meta:
        model = AcademicEvent
        fields = "__all__"


class AcademicAnnouncementSerializer(serializers.ModelSerializer):
    """اطلاعیه آموزشی."""

    creator_name = serializers.CharField(source="creator.full_name", read_only=True)

    class Meta:
        model = AcademicAnnouncement
        fields = "__all__"
