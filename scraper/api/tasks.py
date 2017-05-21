from __future__ import absolute_import, unicode_literals
import hashlib
import logging

from django.core.cache import caches

from celery import shared_task

import youtube_dl

#  from core import extractor
from cheapcdn import client

logger = logging.getLogger(__name__)
store = caches['progress']


def _md5(text):
    return hashlib.md5(text.encode()).hexdigest()


def info(url, opts=None):
    with youtube_dl.YoutubeDL(opts or {}) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except youtube_dl.utils.DownloadError as err:
            logger.error('Failure Info: %s, %r', url, err)
            raise


@shared_task(autoretry_for=(Exception, ),
             retry_kwargs={'max_retries': 5})
def download(url, opts=None):
    opts = opts or {}

    outfile = opts.pop('outfile', _md5(url))
    is_download = opts.pop('download', True)

    default_opts = {
        'writethumbnail': True,
        'hls_prefer_native': True,
        'outtmpl': '/tmp/{}.%(ext)s'.format(outfile),
        'progress_hooks': [lambda d: store.set(outfile, d)]
    }

    with youtube_dl.YoutubeDL({**opts, **default_opts}) as ydl:
        try:
            result = ydl.extract_info(url, download=is_download)
        except youtube_dl.utils.DownloadError as err:
            logger.error('Failure Download: %s, %r', url, err)
            raise

    outtmpl = result
    if 'entries' in result:
        outtmpl = result['entries'][0]

    outfile = default_opts['outtmpl'] % outtmpl

    if is_download:
        # Upload video and image
        client.cheaper().upfile(outfile)

    result.update({'outfile': outfile})
    return result
