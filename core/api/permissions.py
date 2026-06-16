from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS


def _require_authenticated(user):
    if not getattr(user, "is_authenticated", False):
        raise NotAuthenticated()


class IsAuthenticatedAccount(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        _require_authenticated(user)
        if not hasattr(user, "account"):
            raise PermissionDenied("حساب کاربری معتبر یافت نشد.")
        return True


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        _require_authenticated(user)
        return user.has_role("admin")


class IsStudentRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        _require_authenticated(user)
        return user.has_role("student")


class IsTeacherRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        _require_authenticated(user)
        return user.has_role("teacher")


class IsEmployeeRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        _require_authenticated(user)
        return user.has_role("employee")


class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method in SAFE_METHODS:
            _require_authenticated(user)
            return True
        _require_authenticated(user)
        return user.has_role("admin")


class AdminWriteAuthenticatedRead(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        _require_authenticated(user)
        if request.method in SAFE_METHODS:
            return True
        return user.has_role("admin") or user.has_role("staff")


class IsOwnerStudentOrStaff(BasePermission):
    """Object-level: student sees own records; staff/admin see all."""

    student_field = "student"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            raise NotAuthenticated()
        if user.has_role("admin") or user.has_role("staff") or user.has_role("employee"):
            return True
        student = getattr(obj, self.student_field, None)
        if student is None:
            return False
        person = user.person
        return hasattr(person, "student_profile") and person.student_profile.pk == student.pk
