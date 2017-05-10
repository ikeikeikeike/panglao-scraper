from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        db_index=False)

    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        db_index=True)

    def __str__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    class Meta:
        ordering = ["-id"]
        abstract = True
        managed = False
