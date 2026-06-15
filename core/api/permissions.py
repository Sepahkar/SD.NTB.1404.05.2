from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAccount(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return getattr(user, "is_authenticated", False) and hasattr(user, "account")


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return getattr(user, "is_authenticated", False) and user.has_role("admin")


class IsStudentRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return getattr(user, "is_authenticated", False) and user.has_role("student")


class IsTeacherRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return getattr(user, "is_authenticated", False) and user.has_role("teacher")


class IsEmployeeRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return getattr(user, "is_authenticated", False) and user.has_role("employee")


class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return getattr(request.user, "is_authenticated", False)
        user = request.user
        return getattr(user, "is_authenticated", False) and user.has_role("admin")


class AdminWriteAuthenticatedRead(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.has_role("admin") or user.has_role("staff")


class IsOwnerStudentOrStaff(BasePermission):
    """Object-level: student sees own records; staff/admin see all."""

    student_field = "student"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False
        if user.has_role("admin") or user.has_role("staff") or user.has_role("employee"):
            return True
        student = getattr(obj, self.student_field, None)
        if student is None:
            return False
        person = user.person
        return hasattr(person, "student_profile") and person.student_profile.pk == student.pk
