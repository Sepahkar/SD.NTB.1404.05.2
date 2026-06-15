from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from core.models import AuthAccount, AuthRole, Department, Person, Student


class Command(BaseCommand):
    help = "ایجاد نقش‌های پایه و یک کاربر دانشجوی نمونه برای تست API"

    def handle(self, *args, **options):
        roles = [
            ("admin", "مدیر سیستم"),
            ("staff", "کارمند اداری"),
            ("student", "دانشجو"),
            ("teacher", "استاد"),
            ("employee", "کارمند"),
        ]
        for code, name in roles:
            AuthRole.objects.get_or_create(code=code, defaults={"name": name})
            self.stdout.write(f"Role ready: {code}")

        person, created = Person.objects.get_or_create(
            username="demo_student",
            defaults={
                "password": make_password("demo1234"),
                "national_code": "0012345678",
                "first_name": "دانشجو",
                "last_name": "نمونه",
            },
        )
        if not created:
            person.password = make_password("demo1234")
            person.save(update_fields=["password"])

        account, _ = AuthAccount.objects.update_or_create(
            username="demo_student",
            defaults={
                "person": person,
                "email": "demo@ntbiau.ac.ir",
                "password_hash": make_password("demo1234"),
            },
        )
        student_role = AuthRole.objects.get(code="student")
        account.roles.set([student_role])

        dept, _ = Department.objects.get_or_create(
            department_code="DEMO",
            defaults={"department_title": "دانشکده نمونه"},
        )
        Student.objects.get_or_create(
            student_number="1400123456",
            defaults={"person": person, "department": dept},
        )

        self.stdout.write(self.style.SUCCESS(
            "\nDemo user created:\n"
            "  username: demo_student\n"
            "  password: demo1234\n"
            "  login:    POST /api/v1/auth/login/\n"
        ))
