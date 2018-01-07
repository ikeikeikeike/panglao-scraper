from django.core.management.base import BaseCommand

from lifecycle.adapter import do as adapter


class Command(BaseCommand):
    def handle(self, *args, **options):
        life = adapter.Lifecycle(keep=4)
        life.samsara()
