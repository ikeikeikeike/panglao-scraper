import django
from django.apps import AppConfig
from django.db import transaction

from core import logging

from . import base


logger = logging.getLogger(__name__)


class LifecycleConfig(AppConfig):
    name = 'lifecycle'
    verbose_name = "Lifecycle"

    def ready(self):
        try:
            self._load_worker()
        except (
            django.db.utils.OperationalError,
            django.db.utils.ProgrammingError
        ) as err:
            logger.error(err)

    def _load_worker(self):
        objs = self.get_model('worker').objects

        with transaction.atomic():
            w, _ = objs.get_or_create(host=base.host)

        w.name = base.fqdn
        w.save()
