from django import http
from django.conf import settings
from django.core.cache import caches

from . import models


def alives(request):
    workers = models.Worker.objects.all()
    return http.JsonResponse({'root': list(workers)})
