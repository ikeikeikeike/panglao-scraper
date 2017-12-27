from django import http

from . import models


def alives(request):
    qs = models.Worker.objects.filter(usable=True).values('name', 'host')
    return http.JsonResponse({'root': list(qs)})
