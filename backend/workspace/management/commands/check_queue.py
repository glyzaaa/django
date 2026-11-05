from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'FIFO queue goals; failures are expected before the student solution.'

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        call_command("test", *['challenge.test_queue'], interactive=False, verbosity=options["verbosity"])
