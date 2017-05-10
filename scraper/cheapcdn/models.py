from __future__ import unicode_literals

from django.db import models

from core.models import BaseModel


class Node(BaseModel):
    url = models.CharField(max_length=255)
    alive = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'nodes'


class Object(BaseModel):
    id = models.BigAutoField(primary_key=True)
    node = models.ForeignKey(Node, db_index=True)
    url = models.TextField(db_index=True)

    class Meta:
        db_table = 'objects'
