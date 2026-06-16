import secrets
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import AuthAccount, AuthSession


class AuthUser:
    """Lightweight user object attached to request.user for DRF."""

    def __init__(self, account: AuthAccount):
        self.account = account
        self.pk = account.pk
        self.id = account.pk
        self.username = account.username
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = True
        self.is_staff = account.roles.filter(code__in=("admin", "staff")).exists()
        self.is_superuser = account.roles.filter(code="admin").exists()

    @property
    def person(self):
        return self.account.person

    def has_role(self, code: str) -> bool:
        return self.account.roles.filter(code=code, is_active=True).exists()

    def __str__(self):
        return self.username


class AuthSessionTokenAuthentication(BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            return None

        if not auth_header.startswith(f"{self.keyword} "):
            raise AuthenticationFailed(
                "فرمت هدر Authorization نامعتبر است. از «Token <session_key>» استفاده کنید."
            )

        token = auth_header[len(self.keyword) + 1 :].strip()
        if not token:
            raise AuthenticationFailed("توکن خالی است.")

        session = (
            AuthSession.objects.filter(session_key=token, expires_at__gt=timezone.now())
            .select_related("account", "account__person")
            .first()
        )
        if not session:
            raise AuthenticationFailed("توکن نامعتبر یا منقضی شده است.")

        return AuthUser(session.account), token

    def authenticate_header(self, request):
        return self.keyword


class AuthSessionAuthentication(SessionAuthentication):
    """Session auth via Django cookie — only when no Authorization header is sent."""

    def authenticate(self, request):
        # If client sends Authorization, token auth must handle it — do not fall back to cookie.
        if request.META.get("HTTP_AUTHORIZATION"):
            return None

        account_id = request.session.get("auth_account_id")
        if not account_id:
            return None

        account = (
            AuthAccount.objects.filter(pk=account_id)
            .select_related("person")
            .prefetch_related("roles")
            .first()
        )
        if not account:
            return None

        return AuthUser(account), None


def create_auth_session(account: AuthAccount, request, days: int = 7) -> AuthSession:
    session_key = secrets.token_hex(32)
    ip = request.META.get("REMOTE_ADDR")
    return AuthSession.objects.create(
        account=account,
        session_key=session_key,
        ip_address=ip,
        expires_at=timezone.now() + timedelta(days=days),
    )


def verify_account_password(account: AuthAccount, raw_password: str) -> bool:
    return check_password(raw_password, account.password_hash)


def set_account_password(account: AuthAccount, raw_password: str) -> None:
    account.password_hash = make_password(raw_password)
    account.save(update_fields=["password_hash"])
