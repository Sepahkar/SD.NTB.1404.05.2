"""سریالایزرهای احراز هویت و موجودیت‌های Auth."""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import AuthAccount, AuthAccountRole, AuthRole, AuthSession


class AuthRoleSerializer(serializers.ModelSerializer):
    """نقش کاربری (student، admin، teacher و ...)."""

    class Meta:
        model = AuthRole
        fields = "__all__"


class AuthAccountSerializer(serializers.ModelSerializer):
    """اطلاعات حساب کاربری شامل نقش‌ها."""

    role_codes = serializers.SerializerMethodField(help_text="لیست کدهای نقش فعال")
    person_name = serializers.CharField(source="person.full_name", read_only=True, help_text="نام کامل شخص")

    class Meta:
        model = AuthAccount
        fields = ["id", "person", "person_name", "username", "email", "role_codes"]
        read_only_fields = fields

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_role_codes(self, obj):
        return list(obj.roles.filter(is_active=True).values_list("code", flat=True))


class AuthAccountCreateSerializer(serializers.ModelSerializer):
    """ایجاد حساب کاربری جدید (فقط مدیر)."""

    password = serializers.CharField(write_only=True, help_text="رمز عبور حساب")
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="لیست شناسه نقش‌ها برای تخصیص",
    )

    class Meta:
        model = AuthAccount
        fields = ["id", "person", "username", "email", "password", "role_ids"]

    def create(self, validated_data):
        from django.contrib.auth.hashers import make_password

        role_ids = validated_data.pop("role_ids", [])
        password = validated_data.pop("password")
        account = AuthAccount.objects.create(
            **validated_data,
            password_hash=make_password(password),
        )
        if role_ids:
            roles = AuthRole.objects.filter(id__in=role_ids)
            account.roles.set(roles)
        return account


class AuthSessionSerializer(serializers.ModelSerializer):
    """نشست فعال احراز هویت."""

    username = serializers.CharField(source="account.username", read_only=True, help_text="نام کاربری")

    class Meta:
        model = AuthSession
        fields = ["id", "account", "username", "session_key", "ip_address", "expires_at"]
        read_only_fields = ["session_key"]


class AuthAccountRoleSerializer(serializers.ModelSerializer):
    """تخصیص نقش به حساب کاربری."""

    account_username = serializers.CharField(source="account.username", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = AuthAccountRole
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    """ورودی سرویس login."""

    username = serializers.CharField(help_text="نام کاربری")
    password = serializers.CharField(write_only=True, help_text="رمز عبور")


class LoginResponseSerializer(serializers.Serializer):
    """پاسخ موفق login."""

    token = serializers.CharField(help_text="توکن نشست — در هدر Authorization: Token <token>")
    expires_at = serializers.DateTimeField(help_text="زمان انقضای توکن")
    account = AuthAccountSerializer(help_text="اطلاعات حساب کاربری")


class MeResponseSerializer(serializers.Serializer):
    """پاسخ سرویس me — پروفایل کاربر جاری."""

    account = AuthAccountSerializer(help_text="اطلاعات حساب")
    person = serializers.DictField(help_text="اطلاعات شخص")
    student = serializers.DictField(allow_null=True, help_text="پروفایل دانشجو (در صورت وجود)")
    teacher = serializers.DictField(allow_null=True, help_text="پروفایل استاد (در صورت وجود)")
    employee = serializers.DictField(allow_null=True, help_text="پروفایل کارمند (در صورت وجود)")


class PasswordResetSerializer(serializers.Serializer):
    """ورودی بازیابی رمز عبور."""

    username = serializers.CharField(help_text="نام کاربری")
    security_answer = serializers.CharField(help_text="پاسخ سوال امنیتی")
    new_password = serializers.CharField(write_only=True, min_length=6, help_text="رمز عبور جدید (حداقل ۶ کاراکتر)")
