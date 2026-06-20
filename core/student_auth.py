"""Server-side auth helpers for student panel views."""

from django.shortcuts import redirect

from core.models import AuthAccount, Student


def get_session_account(request):
    account_id = request.session.get("auth_account_id")
    if not account_id:
        return None
    return (
        AuthAccount.objects.filter(pk=account_id)
        .select_related("person")
        .prefetch_related("roles")
        .first()
    )


def get_session_student(request):
    account = get_session_account(request)
    if not account:
        return None, None
    person = account.person
    if not hasattr(person, "student_profile"):
        return account, None
    return account, person.student_profile


def require_student_session(view_func):
    def wrapper(request, *args, **kwargs):
        account, student = get_session_student(request)
        if not account:
            return redirect("/")
        if student is None and kwargs.get("require_student", True):
            return redirect("/")
        request.auth_account = account
        request.student_profile = student
        return view_func(request, *args, **kwargs)

    return wrapper
