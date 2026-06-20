from django.shortcuts import redirect, render
from django.views import View

from core.frontend_registry import FRONTEND_PAGES
from core.services import page_data as pd
from core.student_auth import get_session_account, get_session_student


class AddDrop2RedirectView(View):
    def get(self, request):
        return redirect("/add-drop/")


class StudentTemplateView(View):
    slug: str = ""
    template_name: str = ""
    require_student: bool = True
    data_loader = None

    def get(self, request):
        page = FRONTEND_PAGES.get(self.slug)
        if not page:
            return redirect("/")

        account, student = get_session_student(request)
        if not account:
            return redirect("/")
        if self.require_student and not student:
            return redirect("/")

        context = {
            "slug": self.slug,
            "page_css": f"/{self.slug}/style.css",
            "active_slug": self.slug,
            "account": account,
            "student": student,
            "person": account.person,
        }

        if self.data_loader:
            if student is not None:
                context["page_data"] = self.data_loader(student)
            else:
                context["page_data"] = self.data_loader()

        return render(request, self.template_name, context)


class TeachersPageView(StudentTemplateView):
    slug = "teachers"
    template_name = "student/teachers.html"
    require_student = False

    def get(self, request):
        page = FRONTEND_PAGES.get(self.slug)
        if not page:
            return redirect("/")
        account, student = get_session_student(request)
        if not account:
            return redirect("/")
        context = {
            "slug": self.slug,
            "page_css": f"/{self.slug}/style.css",
            "active_slug": self.slug,
            "account": account,
            "student": student,
            "person": account.person,
            "page_data": pd.get_teachers_data(),
        }
        return render(request, self.template_name, context)


class FullTranscriptPageView(StudentTemplateView):
    slug = "full-transcript"
    template_name = "student/full_transcript.html"
    data_loader = staticmethod(pd.get_full_transcript_data)


class SemesterTranscriptPageView(StudentTemplateView):
    slug = "semester-transcript"
    template_name = "student/semester_transcript.html"
    data_loader = staticmethod(pd.get_semester_transcript_data)


class GradesPageView(StudentTemplateView):
    slug = "grades"
    template_name = "student/grades.html"
    data_loader = staticmethod(pd.get_grades_data)


class FinancialPageView(StudentTemplateView):
    slug = "financial"
    template_name = "student/financial.html"
    data_loader = staticmethod(pd.get_financial_data)


class DebtsPageView(StudentTemplateView):
    slug = "debts"
    template_name = "student/debts.html"
    data_loader = staticmethod(pd.get_financial_data)


class PaymentHistoryPageView(StudentTemplateView):
    slug = "payment-history"
    template_name = "student/payment_history.html"
    data_loader = staticmethod(pd.get_payment_history_data)


class AdminFinancialPageView(StudentTemplateView):
    slug = "admin-financial"
    template_name = "student/admin_financial.html"
    require_student = False

    def get(self, request):
        account = get_session_account(request)
        if not account:
            return redirect("/")
        if not account.roles.filter(code="admin").exists():
            return redirect("/financial/")
        context = {
            "slug": self.slug,
            "page_css": f"/{self.slug}/style.css",
            "active_slug": self.slug,
            "account": account,
            "person": account.person,
            "page_data": {"admin_view": True},
        }
        return render(request, self.template_name, context)
