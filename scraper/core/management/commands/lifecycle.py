from django.db import transaction
from django.core.management.base import BaseCommand


from cheapcdn import client
from cheapcdn import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        objects = models.Node.objects

        with transaction.atomic():
            node, _ = objects.get_or_create(host=client.extract_host())
        node.free = client.extract_free()
        node.save()
