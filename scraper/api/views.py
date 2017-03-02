import base64

from django import http

from . import tasks
from . import cache


def info(request, encoded):
    url = base64.b64decode(encoded).decode()
    result = tasks.download(url, opts={'download': False})
    return http.JsonResponse(result)


def progress(request, encoded):
    filename = base64.b64decode(encoded).decode()
    return http.JsonResponse(cache.get(filename) or {})


def download(request, encoded):
    url = base64.b64decode(encoded).decode()
    tasks.download.delay(url)
    return http.JsonResponse({})
