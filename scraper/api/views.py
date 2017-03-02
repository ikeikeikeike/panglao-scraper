import base64
import logging

from django import http

import youtube_dl

from core import extractor

logger = logging.getLogger(__name__)

global_opts = {
    'outtmpl': '/tmp/%(title)s-%(id)s.%(ext)s',
    'format': 'bestaudio/best',
}


def info(request, encoded):
    url = base64.b64decode(encoded).decode()
    result = _download(url, {'download': False})
    return http.JsonResponse(result)


def download(request, encoded):
    url = base64.b64decode(encoded).decode()
    result = _download(url)
    return http.JsonResponse(result)


def _download(url, opts=None):
    opts = opts or {}
    dl = opts.pop('download', True)

    with youtube_dl.YoutubeDL(opts or global_opts) as ydl:
        try:
            result = ydl.extract_info(url, download=dl)
        except youtube_dl.utils.DownloadError as err:
            logger.error('Failure Info: %s', url)
            raise

    if not result.get('thumbnail'):
        image = extractor.Image(url)
        result.update({'thumbnail': image.general_choice()})

    result.update({'outputfile': global_opts['outtmpl'] % result})
    return result
