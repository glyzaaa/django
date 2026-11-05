from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Both student data-structure goals.'

    def handle(self, *args, **options):
        self.stdout.write(self.help)
        call_command("test", *['challenge'], interactive=False, verbosity=options["verbosity"])
