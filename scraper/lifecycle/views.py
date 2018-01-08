from django import http
from django.conf import settings
from django.urls import reverse_lazy

from . import models


info_path = reverse_lazy('api:info', args=[''])
stream_path = reverse_lazy('api:stream', args=[''])
port = 8000 if settings.ENVIRONMENT == 'local' else 80


def alives(request):
    qs = models.Worker.workers.alives().all()

    root = []
    for worker in qs:
        args = [request.scheme, worker.host, port]

        root.append({
            'name': worker.name, 'host': worker.host,
            'info': '{}://{}:{}{}'.format(*(args + [info_path])),
            'stream': '{}://{}:{}{}'.format(*(args + [stream_path])),
        })

    return http.JsonResponse({'root': root})
