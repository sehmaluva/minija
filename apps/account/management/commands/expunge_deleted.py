from django.core.management.base import BaseCommand

from apps.account.models.models import AccountDeletion


class Command(BaseCommand):

    help = "Expunge accounts deleted more than 48 hours ago."

    def handle(self, *args, **options):
        count = AccountDeletion.expunge()
        print("{0} expunged.".format(count))
