from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Application and account checks; expected to pass in the starter.'

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        call_command("test", *['tests'], interactive=False, verbosity=options["verbosity"])
