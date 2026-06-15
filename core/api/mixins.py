from rest_framework import viewsets


class StudentScopedQuerysetMixin:
    """Filter list/detail queryset to current student unless admin/staff."""

    student_lookup = "student"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            return qs.none()
        if user.has_role("admin") or user.has_role("staff") or user.has_role("employee"):
            return qs
        person = user.person
        if hasattr(person, "student_profile"):
            return qs.filter(**{self.student_lookup: person.student_profile})
        return qs.none()
