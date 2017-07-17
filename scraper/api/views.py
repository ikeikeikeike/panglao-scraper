import uuid
import base64

from django import http
from django.core.cache import caches

from cheapcdn import client

from . import tasks

store = caches['progress']


def info(request, encoded):
    url = base64.b64decode(encoded).decode()
    return http.JsonResponse(tasks.info(url))


def nodeinfo(request):
    infos = list(client.CheapCDN().nodeinfo())
    return http.JsonResponse({'info': infos})


def download(request, encoded):
    url = base64.b64decode(encoded).decode()
    outfile = str(uuid.uuid4())

    tasks.download.delay(url, opts=dict(outfile=outfile))
    res = tasks.download(url, opts=dict(outfile=outfile, download=False))
    return http.JsonResponse(res)


def progress(request, encoded):
    key = base64.b64decode(encoded).decode()
    return http.JsonResponse(store.get(key) or {})


def findfile(request, encoded):
    key = base64.b64decode(encoded).decode()
    files = list(client.CheapCDN().findprefix(key))
    return http.JsonResponse({'file': files})


def removefile(request, encoded):
    key = base64.b64decode(encoded).decode()
    client.CheapCDN().rmfile(key)
    return http.JsonResponse({})
