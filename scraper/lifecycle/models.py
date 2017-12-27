from __future__ import unicode_literals

from django.db import models

from core.models import BaseModel


class Worker(BaseModel):
    name = models.CharField(max_length=255, null=True, unique=True)
    host = models.GenericIPAddressField()

    usable = models.BooleanField(default=True)

    class Meta:
        db_table = 'workers'
