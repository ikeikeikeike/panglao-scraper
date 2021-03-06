from __future__ import unicode_literals

from django.db import models

from core.models import BaseModel


class Node(BaseModel):
    #  name = models.CharField(max_length=255, null=True, unique=True)
    host = models.CharField(max_length=255)
    free = models.BigIntegerField(null=True)
    alive = models.BooleanField(default=True, db_index=True)
    choiceable = models.BooleanField(default=True)
    #  sweepable = models.BooleanField(default=True)
    provider = models.SlugField(default='minio')

    class Meta:
        db_table = 'nodes'


class Object(BaseModel):
    id = models.BigAutoField(primary_key=True)
    node = models.ForeignKey(Node, null=True, db_index=True)
    name = models.TextField(db_index=True)

    class Meta:
        db_table = 'objects'
