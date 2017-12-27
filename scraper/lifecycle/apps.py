import socket

import django
from django.apps import AppConfig
from django.db import transaction

import netifaces as ni

from core import logging


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
            w, _ = objs.get_or_create(host=extract_host())

        w.name = socket.getfqdn()
        w.save()


def extract_host():
    try:
        return ni.ifaddresses('eth1')[2][0]['addr']
    except ValueError:
        return '127.0.0.1'
