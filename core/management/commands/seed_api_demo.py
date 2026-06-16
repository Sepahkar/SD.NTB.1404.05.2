from django.core.management.base import BaseCommand

from core.seed.demo_data import seed_demo_data


class Command(BaseCommand):
    help = "ایجاد داده‌های نمونه کامل برای تست API و فرانت‌اند (idempotent)"

    def handle(self, *args, **options):
        seed_demo_data(stdout=self.stdout)
