from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task

import youtube_dl
from core import extractor

from . import cache

logger = logging.getLogger(__name__)

global_opts = {
    'outtmpl': '/tmp/%(title)s-%(id)s.%(ext)s',
    'progress_hooks': [],
}


@shared_task
def download(url, opts=None):
    opts = opts or global_opts
    opts = {**opts, **{'progress_hooks': [lambda d: cache.set(url, d)]}}

    dl = opts.pop('download', True)

    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            result = ydl.extract_info(url, download=dl)
        except youtube_dl.utils.DownloadError as err:
            logger.error('Failure Info: %s, %r', url, err)
            raise

    if not result.get('thumbnail'):
        image = extractor.Image(url)
        result.update({'thumbnail': image.general_choice()})

    outtmpl = result
    if 'entries' in result:
        outtmpl = result['entries'][0]

    result.update({'outputfile': global_opts['outtmpl'] % outtmpl})
    return result
