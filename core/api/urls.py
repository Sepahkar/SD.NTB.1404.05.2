from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.api.views.academic import (
    AttendanceViewSet,
    ClassOfferViewSet,
    ClassViewSet,
    ExamInvigilatorViewSet,
    ExamResultViewSet,
    ExamViewSet,
    LessonViewSet,
    PrerequisiteWarningViewSet,
    TeacherEvaluationViewSet,
    TranscriptViewSet,
)
from core.api.views.auth import LoginAPIView, LogoutAPIView, MeAPIView, PasswordResetAPIView
from core.api.views.composite import (
    AddDropPageAPIView,
    CourseSelectionPageAPIView,
    DashboardPageAPIView,
    FinancialPageAPIView,
    FullTranscriptPageAPIView,
    GradeObjectionPageAPIView,
    GradesPageAPIView,
    LeaveRequestPageAPIView,
    LoanRequestPageAPIView,
    PaymentHistoryPageAPIView,
    SemesterTranscriptPageAPIView,
    StudentRequestsPageAPIView,
    TeachersPageAPIView,
)
from core.api.views.finance import (
    AcademicLeaveRequestViewSet,
    DormitoryRequestViewSet,
    LoanViewSet,
    ScholarshipViewSet,
    StudentPaymentsViewSet,
    StudentRequestViewSet,
)
from core.api.views.library_misc import (
    AcademicAnnouncementViewSet,
    AcademicEventViewSet,
    AcademicProgramViewSet,
    AuthAccountRoleViewSet,
    AuthAccountViewSet,
    AuthRoleViewSet,
    AuthSessionViewSet,
    BookViewSet,
    CompanyViewSet,
    DocumentStudentViewSet,
    InternshipViewSet,
    LibraryBookLendingViewSet,
    LibraryReserveViewSet,
)
from core.api.views.lookup import (
    ConstValueViewSet,
    DepartmentViewSet,
    EducationBranchViewSet,
    TendencyViewSet,
    TermViewSet,
)
from core.api.views.person import (
    EmailAddressViewSet,
    PersonSkillViewSet,
    PersonViewSet,
    PhoneNumberViewSet,
    PostalAddressViewSet,
)
from core.api.views.profiles import (
    EmployeeViewSet,
    StudentViewSet,
    TeacherResearchInterestViewSet,
    TeacherViewSet,
)

router = DefaultRouter()

# Lookup / reference data
router.register(r"const-values", ConstValueViewSet, basename="const-value")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"education-branches", EducationBranchViewSet, basename="education-branch")
router.register(r"tendencies", TendencyViewSet, basename="tendency")
router.register(r"terms", TermViewSet, basename="term")

# Person & contact
router.register(r"persons", PersonViewSet, basename="person")
router.register(r"phone-numbers", PhoneNumberViewSet, basename="phone-number")
router.register(r"email-addresses", EmailAddressViewSet, basename="email-address")
router.register(r"person-skills", PersonSkillViewSet, basename="person-skill")
router.register(r"postal-addresses", PostalAddressViewSet, basename="postal-address")

# Profiles
router.register(r"teachers", TeacherViewSet, basename="teacher")
router.register(r"teacher-research-interests", TeacherResearchInterestViewSet, basename="teacher-research-interest")
router.register(r"students", StudentViewSet, basename="student")
router.register(r"employees", EmployeeViewSet, basename="employee")

# Academic
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"classes", ClassViewSet, basename="class")
router.register(r"class-offers", ClassOfferViewSet, basename="class-offer")
router.register(r"exams", ExamViewSet, basename="exam")
router.register(r"exam-invigilators", ExamInvigilatorViewSet, basename="exam-invigilator")
router.register(r"exam-results", ExamResultViewSet, basename="exam-result")
router.register(r"attendances", AttendanceViewSet, basename="attendance")
router.register(r"transcripts", TranscriptViewSet, basename="transcript")
router.register(r"teacher-evaluations", TeacherEvaluationViewSet, basename="teacher-evaluation")
router.register(r"prerequisite-warnings", PrerequisiteWarningViewSet, basename="prerequisite-warning")

# Finance & requests
router.register(r"student-payments", StudentPaymentsViewSet, basename="student-payment")
router.register(r"student-requests", StudentRequestViewSet, basename="student-request")
router.register(r"academic-leave-requests", AcademicLeaveRequestViewSet, basename="academic-leave-request")
router.register(r"scholarships", ScholarshipViewSet, basename="scholarship")
router.register(r"dormitory-requests", DormitoryRequestViewSet, basename="dormitory-request")
router.register(r"loans", LoanViewSet, basename="loan")

# Library & misc
router.register(r"books", BookViewSet, basename="book")
router.register(r"library-book-lendings", LibraryBookLendingViewSet, basename="library-book-lending")
router.register(r"library-reserves", LibraryReserveViewSet, basename="library-reserve")
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"internships", InternshipViewSet, basename="internship")
router.register(r"document-students", DocumentStudentViewSet, basename="document-student")
router.register(r"academic-programs", AcademicProgramViewSet, basename="academic-program")
router.register(r"academic-events", AcademicEventViewSet, basename="academic-event")
router.register(r"academic-announcements", AcademicAnnouncementViewSet, basename="academic-announcement")

# Auth entities (admin)
router.register(r"auth-roles", AuthRoleViewSet, basename="auth-role")
router.register(r"auth-accounts", AuthAccountViewSet, basename="auth-account")
router.register(r"auth-sessions", AuthSessionViewSet, basename="auth-session")
router.register(r"auth-account-roles", AuthAccountRoleViewSet, basename="auth-account-role")

urlpatterns = [
    # Authentication
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/me/", MeAPIView.as_view(), name="auth-me"),
    path("auth/password/reset/", PasswordResetAPIView.as_view(), name="auth-password-reset"),

    # Composite page APIs (one call per frontend page)
    path("pages/dashboard/", DashboardPageAPIView.as_view(), name="page-dashboard"),
    path("pages/semester-transcript/", SemesterTranscriptPageAPIView.as_view(), name="page-semester-transcript"),
    path("pages/full-transcript/", FullTranscriptPageAPIView.as_view(), name="page-full-transcript"),
    path("pages/grades/", GradesPageAPIView.as_view(), name="page-grades"),
    path("pages/course-selection/", CourseSelectionPageAPIView.as_view(), name="page-course-selection"),
    path("pages/add-drop/", AddDropPageAPIView.as_view(), name="page-add-drop"),
    path("pages/financial/", FinancialPageAPIView.as_view(), name="page-financial"),
    path("pages/payment-history/", PaymentHistoryPageAPIView.as_view(), name="page-payment-history"),
    path("pages/loan-request/", LoanRequestPageAPIView.as_view(), name="page-loan-request"),
    path("pages/student-requests/", StudentRequestsPageAPIView.as_view(), name="page-student-requests"),
    path("pages/leave-request/", LeaveRequestPageAPIView.as_view(), name="page-leave-request"),
    path("pages/teachers/", TeachersPageAPIView.as_view(), name="page-teachers"),
    path("pages/grade-objection/", GradeObjectionPageAPIView.as_view(), name="page-grade-objection"),

    # CRUD resources
    path("", include(router.urls)),
]
