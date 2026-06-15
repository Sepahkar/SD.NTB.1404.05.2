from rest_framework import viewsets

from core.api.openapi.decorators import tagged_viewset
from core.api.openapi.tags import TAG_PERSON
from core.api.permissions import AdminWriteAuthenticatedRead, IsAdminRole
from core.api.serializers.person import (
    EmailAddressSerializer,
    PersonCreateSerializer,
    PersonSerializer,
    PersonSkillSerializer,
    PhoneNumberSerializer,
    PostalAddressSerializer,
)
from core.models import EmailAddress, Person, PersonSkill, PhoneNumber, PostalAddress


@tagged_viewset(TAG_PERSON, "اشخاص")
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    permission_classes = [IsAdminRole]
    search_fields = ["username", "national_code", "first_name", "last_name", "full_name"]

    def get_serializer_class(self):
        if self.action == "create":
            return PersonCreateSerializer
        return PersonSerializer


@tagged_viewset(TAG_PERSON, "شماره تلفن‌ها")
class PhoneNumberViewSet(viewsets.ModelViewSet):
    queryset = PhoneNumber.objects.select_related("person").all()
    serializer_class = PhoneNumberSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["person"]


@tagged_viewset(TAG_PERSON, "آدرس‌های ایمیل")
class EmailAddressViewSet(viewsets.ModelViewSet):
    queryset = EmailAddress.objects.select_related("person").all()
    serializer_class = EmailAddressSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["person", "email_type", "is_primary"]


@tagged_viewset(TAG_PERSON, "مهارت‌های شخص")
class PersonSkillViewSet(viewsets.ModelViewSet):
    queryset = PersonSkill.objects.select_related("person").all()
    serializer_class = PersonSkillSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["person", "level"]


@tagged_viewset(TAG_PERSON, "آدرس‌های پستی")
class PostalAddressViewSet(viewsets.ModelViewSet):
    queryset = PostalAddress.objects.select_related("person").all()
    serializer_class = PostalAddressSerializer
    permission_classes = [AdminWriteAuthenticatedRead]
    filterset_fields = ["person"]
