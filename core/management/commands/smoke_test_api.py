import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run curl-based API smoke tests against a running server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            default="http://127.0.0.1:8000",
            help="Server base URL (default: http://127.0.0.1:8000)",
        )
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Run seed_api_demo before smoke tests",
        )

    def handle(self, *args, **options):
        if options["seed"]:
            self.stdout.write("Running seed_api_demo...")
            from core.seed.demo_data import seed_demo_data

            seed_demo_data(stdout=self.stdout)

        script = Path(__file__).resolve().parents[3] / "scripts" / "smoke_test_api.sh"
        if not script.exists():
            self.stderr.write(self.style.ERROR(f"Script not found: {script}"))
            sys.exit(1)

        result = subprocess.run(
            ["bash", str(script), options["base_url"]],
            cwd=script.parents[1],
        )
        if result.returncode != 0:
            sys.exit(result.returncode)
        self.stdout.write(self.style.SUCCESS("All smoke tests passed."))
