"""سریالایزرهای شخص و اطلاعات تماس."""

from rest_framework import serializers

from core.models import (
    EmailAddress,
    Person,
    PersonSkill,
    PhoneNumber,
    PostalAddress,
)


class PersonSerializer(serializers.ModelSerializer):
    """اطلاعات شخص — بدون رمز و پاسخ امنیتی."""

    class Meta:
        model = Person
        exclude = ["password", "security_answer"]
        read_only_fields = ["failed_login", "last_login_at", "account_locked"]


class PersonCreateSerializer(serializers.ModelSerializer):
    """ایجاد شخص جدید."""

    password = serializers.CharField(write_only=True, required=False, help_text="رمز عبور (اختیاری)")

    class Meta:
        model = Person
        exclude = ["security_answer"]
        read_only_fields = ["failed_login", "last_login_at", "account_locked"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        person = Person.objects.create(**validated_data)
        if password:
            from django.contrib.auth.hashers import make_password

            person.password = make_password(password)
            person.save(update_fields=["password"])
        return person


class PersonBriefSerializer(serializers.ModelSerializer):
    """نمای خلاصه شخص."""

    class Meta:
        model = Person
        fields = ["id", "username", "first_name", "last_name", "full_name", "national_code"]


class PhoneNumberSerializer(serializers.ModelSerializer):
    """شماره تلفن شخص."""

    class Meta:
        model = PhoneNumber
        fields = "__all__"


class EmailAddressSerializer(serializers.ModelSerializer):
    """آدرس ایمیل شخص."""

    class Meta:
        model = EmailAddress
        fields = "__all__"


class PersonSkillSerializer(serializers.ModelSerializer):
    """مهارت شخص."""

    class Meta:
        model = PersonSkill
        fields = "__all__"


class PostalAddressSerializer(serializers.ModelSerializer):
    """آدرس پستی شخص."""

    class Meta:
        model = PostalAddress
        fields = "__all__"
