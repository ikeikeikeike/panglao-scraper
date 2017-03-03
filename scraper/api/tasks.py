from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task

import youtube_dl
from core import extractor

from . import cache

logger = logging.getLogger(__name__)


@shared_task
def download(url, opts=None):
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


global_opts = {
    'outtmpl': '/tmp/%(title)s-%(id)s.%(ext)s',
    'format': 'bestaudio/best',
    'progress_hooks': [
        lambda d: cache.set(d['filename'], d),
    ],
}
