from rest_framework import viewsets

from core.api.mixins import StudentScopedQuerysetMixin
from core.api.openapi.decorators import tagged_readonly_viewset, tagged_viewset
from core.api.openapi.tags import TAG_AUTH_ENTITIES, TAG_LIBRARY_MISC
from core.api.permissions import AdminWriteAuthenticatedRead, IsAdminRole, IsOwnerStudentOrStaff
from core.api.serializers.auth import (
    AuthAccountCreateSerializer,
    AuthAccountRoleSerializer,
    AuthAccountSerializer,
    AuthRoleSerializer,
    AuthSessionSerializer,
)
from core.api.serializers.library_misc import (
    AcademicAnnouncementSerializer,
    AcademicEventSerializer,
    AcademicProgramSerializer,
    BookSerializer,
    CompanySerializer,
    DocumentStudentSerializer,
    InternshipSerializer,
    LibraryBookLendingSerializer,
    LibraryReserveSerializer,
)
from core.models import (
    AcademicAnnouncement,
    AcademicEvent,
    AcademicProgram,
    AuthAccount,
    AuthAccountRole,
    AuthRole,
    AuthSession,
    Book,
    Company,
    DocumentStudent,
    Internship,
    LibraryBookLending,
    LibraryResource,
)


@tagged_viewset(TAG_LIBRARY_MISC, "کتاب‌ها")
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    search_fields = ["title", "isbn"]


@tagged_viewset(TAG_LIBRARY_MISC, "امانت کتاب")
class LibraryBookLendingViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = LibraryBookLending.objects.select_related("book", "student", "employee").all()
    serializer_class = LibraryBookLendingSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "book", "is_returned"]


@tagged_viewset(TAG_LIBRARY_MISC, "رزرو منابع کتابخانه")
class LibraryReserveViewSet(viewsets.ModelViewSet):
    queryset = LibraryResource.objects.select_related("person").all()
    serializer_class = LibraryReserveSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["person", "is_returned"]


@tagged_viewset(TAG_LIBRARY_MISC, "شرکت‌ها")
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    search_fields = ["name", "registration_number"]


@tagged_viewset(TAG_LIBRARY_MISC, "کارآموزی")
class InternshipViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = Internship.objects.select_related("student", "company").all()
    serializer_class = InternshipSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "company"]


@tagged_viewset(TAG_LIBRARY_MISC, "مدارک دانشجو")
class DocumentStudentViewSet(StudentScopedQuerysetMixin, viewsets.ModelViewSet):
    queryset = DocumentStudent.objects.select_related("student", "document_type", "verification_status").all()
    serializer_class = DocumentStudentSerializer
    permission_classes = [AdminWriteAuthenticatedRead, IsOwnerStudentOrStaff]
    filterset_fields = ["student", "document_type"]


@tagged_viewset(TAG_LIBRARY_MISC, "برنامه‌های آموزشی")
class AcademicProgramViewSet(viewsets.ModelViewSet):
    queryset = AcademicProgram.objects.select_related("department").all()
    serializer_class = AcademicProgramSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["department", "degree_level"]


@tagged_viewset(TAG_LIBRARY_MISC, "رویدادهای آموزشی")
class AcademicEventViewSet(viewsets.ModelViewSet):
    queryset = AcademicEvent.objects.select_related(
        "event_type", "organizer_person", "host_department", "status"
    ).all()
    serializer_class = AcademicEventSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["event_type", "status", "is_public"]


@tagged_viewset(TAG_LIBRARY_MISC, "اطلاعیه‌های آموزشی")
class AcademicAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = AcademicAnnouncement.objects.select_related(
        "announcement_type", "audience", "status", "creator"
    ).all()
    serializer_class = AcademicAnnouncementSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["announcement_type", "status", "is_urgent"]


@tagged_viewset(TAG_AUTH_ENTITIES, "نقش‌های کاربری")
class AuthRoleViewSet(viewsets.ModelViewSet):
    queryset = AuthRole.objects.all()
    serializer_class = AuthRoleSerializer
    permission_classes = [IsAdminRole]
    search_fields = ["code", "name"]


@tagged_viewset(TAG_AUTH_ENTITIES, "حساب‌های کاربری")
class AuthAccountViewSet(viewsets.ModelViewSet):
    queryset = AuthAccount.objects.select_related("person").prefetch_related("roles").all()
    permission_classes = [IsAdminRole]
    search_fields = ["username", "email"]

    def get_serializer_class(self):
        if self.action == "create":
            return AuthAccountCreateSerializer
        return AuthAccountSerializer


@tagged_readonly_viewset(TAG_AUTH_ENTITIES, "نشست‌های احراز هویت")
class AuthSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuthSession.objects.select_related("account").all()
    serializer_class = AuthSessionSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ["account"]


@tagged_viewset(TAG_AUTH_ENTITIES, "تخصیص نقش به حساب")
class AuthAccountRoleViewSet(viewsets.ModelViewSet):
    queryset = AuthAccountRole.objects.select_related("account", "role", "assigned_by").all()
    serializer_class = AuthAccountRoleSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ["account", "role"]
