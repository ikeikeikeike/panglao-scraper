from __future__ import absolute_import, unicode_literals
import hashlib
import logging

from celery import shared_task

import youtube_dl
from core import extractor

from . import cache

logger = logging.getLogger(__name__)


@shared_task
def download(url, opts=None):
    md5 = hashlib.md5(url.encode()).hexdigest()
    default_opts = {
        'outtmpl': '/tmp/{}.%(ext)s'.format(md5),
        'progress_hooks': [lambda d: cache.set(url, d), lambda d: print(d)]
    }

    opts = opts or {}
    opts = {**opts, **default_opts}

    dl = opts.pop('download', True)

    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            result = ydl.extract_info(url, download=dl)
        except youtube_dl.utils.DownloadError as err:
            logger.error('Failure Info: %s, %r', url, err)
            raise

    if dl is not True and not result.get('thumbnail'):
        image = extractor.Image(url)
        result.update({'thumbnail': image.general_choice()})

    outtmpl = result
    if 'entries' in result:
        outtmpl = result['entries'][0]

    result.update({'outputfile': default_opts['outtmpl'] % outtmpl})
    return result
