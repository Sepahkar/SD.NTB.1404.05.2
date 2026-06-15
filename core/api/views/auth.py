from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.authentication import (
    AuthUser,
    create_auth_session,
    verify_account_password,
)
from core.api.openapi.tags import TAG_AUTHENTICATION
from core.api.permissions import IsAuthenticatedAccount
from core.api.serializers.auth import (
    AuthAccountSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    MeResponseSerializer,
    PasswordResetSerializer,
)
from core.api.serializers.common import DetailResponseSerializer
from core.api.serializers.person import PersonBriefSerializer
from core.api.serializers.profiles import EmployeeSerializer, StudentBriefSerializer, TeacherSerializer
from core.models import AuthAccount, AuthSession, Person


@extend_schema_view(
    post=extend_schema(
        tags=[TAG_AUTHENTICATION],
        summary="ورود به سامانه",
        description=(
            "احراز هویت با نام کاربری و رمز عبور.\n\n"
            "در صورت موفقیت، توکن نشست (session_key) و اطلاعات حساب برگردانده می‌شود.\n"
            "توکن را در هدر Authorization به صورت `Token <session_key>` ارسال کنید.\n\n"
            "خطاهای ممکن: 401 (نام کاربری/رمز اشتباه)، 403 (حساب قفل شده)."
        ),
        request=LoginSerializer,
        responses={200: LoginResponseSerializer},
    ),
)
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        account = (
            AuthAccount.objects.filter(username=username)
            .select_related("person")
            .prefetch_related("roles")
            .first()
        )

        authenticated = False
        if account and verify_account_password(account, password):
            authenticated = True
        elif not account:
            person = Person.objects.filter(username=username).first()
            if person and person.password and check_password(password, person.password):
                account = getattr(person, "auth_account", None)
                if account:
                    authenticated = True

        if not authenticated or not account:
            return Response({"detail": "نام کاربری یا رمز عبور اشتباه است."}, status=status.HTTP_401_UNAUTHORIZED)

        if account.person.account_locked:
            return Response({"detail": "حساب کاربری قفل شده است."}, status=status.HTTP_403_FORBIDDEN)

        session = create_auth_session(account, request)
        request.session["auth_account_id"] = str(account.pk)
        request.session.save()

        account.person.last_login_at = timezone.now()
        account.person.failed_login = 0
        account.person.save(update_fields=["last_login_at", "failed_login"])

        return Response(
            {
                "token": session.session_key,
                "expires_at": session.expires_at,
                "account": AuthAccountSerializer(account).data,
            }
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]
    serializer_class = DetailResponseSerializer

    @extend_schema(
        tags=[TAG_AUTHENTICATION],
        summary="خروج از سامانه",
        description=(
            "ابطال توکن نشست جاری و پاک‌سازی کوکی نشست Django.\n\n"
            "نیاز به احراز هویت دارد. هدر Authorization: Token <session_key>."
        ),
        request=None,
        responses={200: DetailResponseSerializer},
    )
    def post(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Token "):
            token = auth_header[6:].strip()
            AuthSession.objects.filter(session_key=token).delete()
        request.session.flush()
        return Response({"detail": "با موفقیت خارج شدید."})


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_AUTHENTICATION],
        summary="پروفایل کاربر جاری",
        description=(
            "دریافت اطلاعات حساب، شخص و پروفایل‌های مرتبط (دانشجو، استاد، کارمند).\n\n"
            "نیاز به احراز هویت دارد."
        ),
        responses={200: MeResponseSerializer},
    ),
)
class MeAPIView(APIView):
    permission_classes = [IsAuthenticatedAccount]

    def get(self, request):
        user: AuthUser = request.user
        account = user.account
        person = account.person

        student_data = None
        teacher_data = None
        employee_data = None

        if hasattr(person, "student_profile"):
            student_data = StudentBriefSerializer(person.student_profile).data
        if hasattr(person, "teacher_profile"):
            teacher_data = TeacherSerializer(person.teacher_profile).data
        if hasattr(person, "employee_profile"):
            employee_data = EmployeeSerializer(person.employee_profile).data

        return Response(
            {
                "account": AuthAccountSerializer(account).data,
                "person": PersonBriefSerializer(person).data,
                "student": student_data,
                "teacher": teacher_data,
                "employee": employee_data,
            }
        )


@extend_schema_view(
    post=extend_schema(
        tags=[TAG_AUTHENTICATION],
        summary="بازیابی رمز عبور",
        description=(
            "تغییر رمز عبور با استفاده از نام کاربری، پاسخ امنیتی و رمز جدید.\n\n"
            "بدون نیاز به احراز هویت. خطاهای ممکن: 404 (کاربر یافت نشد)، 400 (پاسخ امنیتی اشتباه)."
        ),
        request=PasswordResetSerializer,
        responses={200: DetailResponseSerializer},
    ),
)
class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        security_answer = serializer.validated_data["security_answer"]
        new_password = serializer.validated_data["new_password"]

        person = Person.objects.filter(username=username).first()
        if not person:
            return Response({"detail": "کاربر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        if person.security_answer != security_answer:
            return Response({"detail": "پاسخ امنیتی اشتباه است."}, status=status.HTTP_400_BAD_REQUEST)

        person.password = make_password(new_password)
        person.save(update_fields=["password"])

        account = getattr(person, "auth_account", None)
        if account:
            account.password_hash = make_password(new_password)
            account.save(update_fields=["password_hash"])

        return Response({"detail": "رمز عبور با موفقیت تغییر کرد."})
