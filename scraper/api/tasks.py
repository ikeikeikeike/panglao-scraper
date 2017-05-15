from __future__ import absolute_import, unicode_literals
import hashlib
import logging

from celery import shared_task

import youtube_dl

#  from core import extractor
from cheapcdn import client

from . import cache

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(Exception, ),
             retry_kwargs={'max_retries': 5})
def download(url, opts=None):
    md5 = hashlib.md5(url.encode()).hexdigest()
    default_opts = {
        'writethumbnail': True,
        'hls_prefer_native': True,
        'outtmpl': '/tmp/{}.%(ext)s'.format(md5),
        'progress_hooks': [lambda d: cache.set(url, d)]
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

    outtmpl = result
    if 'entries' in result:
        outtmpl = result['entries'][0]

    outfile = default_opts['outtmpl'] % outtmpl

    # upload movie and image
    dl and client.cheaper().upfile(outfile)

    result.update({'outputfile': outfile})
    return result
