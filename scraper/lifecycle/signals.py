from django.core import signals
from django.dispatch import receiver

from . import models


@receiver(signals.request_started)
def lock_in_request(**kwargs):
    wk = models.Worker.workers.get_by_host()
    wk.busy = True
    wk.save()


@receiver(signals.request_finished)
def lock_after_request(**kwargs):
    wk = models.Worker.workers.get_by_host()
    wk.busy = False
    wk.save()


@receiver(signals.got_request_exception)
def lock_after_exception(**kwargs):
    wk = models.Worker.workers.get_by_host()
    wk.busy = False
    wk.save()
