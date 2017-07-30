import uuid
import base64
import subprocess

from django import http
from django.core.cache import caches

from cheapcdn import client

from . import tasks

store = caches['progress']


def info(request, encoded):
    url = base64.b64decode(encoded).decode()
    root = tasks.info(url)

    if isinstance(root, int):
        return http.JsonResponse({'errno': root})
    return http.JsonResponse({'root': root})


def nodeinfo(request):
    infos = list(client.CheapCDN().nodeinfo())
    return http.JsonResponse({'root': infos})


def abledisk(request):
    boolean = client.CheapCDN().is_abledisk()
    return http.JsonResponse({'root': boolean})


def download(request, encoded):
    url = base64.b64decode(encoded).decode()
    outfile = str(uuid.uuid4())

    tasks.download.delay(url, opts=dict(outfile=outfile))
    root = tasks.download(url, opts=dict(outfile=outfile, download=False))
    return http.JsonResponse({'root': root})


def progress(request, encoded):
    key = base64.b64decode(encoded).decode()
    return http.JsonResponse(store.get(key) or {})


def findfile(request, encoded):
    key = base64.b64decode(encoded).decode()
    files = list(client.CheapCDN().findprefix(key))
    return http.JsonResponse({'root': files})


def removefile(request, encoded):
    key = base64.b64decode(encoded).decode()
    client.CheapCDN().rmfile(key)
    return http.JsonResponse({})


def extractors(request):
    cmd, PIPE = ['youtube-dl', '--list-extractors'], subprocess.PIPE
    r = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return http.JsonResponse({'root': str(r.stdout).strip().split('\n')})
