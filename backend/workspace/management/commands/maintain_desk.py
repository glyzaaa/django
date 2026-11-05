from datetime import timedelta
from django.core.management import BaseCommand, call_command
from django.utils import timezone
from database.models import LoginThrottle


class Command(BaseCommand):
    help = "Remove expired Django sessions and old sign-in throttle records."
    def handle(self, *args, **options):
        call_command("clearsessions")
        count, _ = LoginThrottle.objects.filter(window_start__lt=timezone.now()-timedelta(days=1)).delete()
        self.stdout.write(f"Removed {count} expired throttle record(s).")
