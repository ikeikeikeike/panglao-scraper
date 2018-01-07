from __future__ import unicode_literals

from django.db import models

from core.models import BaseModel

from . import base


class WorkerManager(models.Manager):
    @property
    def qs(self):
        return self.get_queryset()

    def alives(self):
        return self.qs.filter(usable=True, busy=False)

    def get_by_host(self):
        """ returns unique record """
        return self.qs.filter(host=base.host).first()

    def get_by_name(self):
        """ returns unique record """
        return self.qs.filter(name=base.fqdn).first()


class Worker(BaseModel):
    name = models.CharField(max_length=255, null=True, unique=True)
    host = models.GenericIPAddressField()

    usable = models.BooleanField(default=True)
    busy = models.BooleanField(default=False)

    objects = models.Manager()
    workers = WorkerManager()

    class Meta:
        db_table = 'workers'
