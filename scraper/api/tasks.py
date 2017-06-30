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


def _one(result):
    entry = result.pop('entries', [{}])[0]
    return {**result, **entry}


def info(url, opts=None):
    with youtube_dl.YoutubeDL(opts or {}) as ydl:
        try:
            return _one(ydl.extract_info(url, download=False))
        except youtube_dl.utils.DownloadError as err:
            # TODO: remove file
            logger.error('Failure Info: %s, %r', url, err)
            raise


# TODO: count-up zero and comment in if fixed TODO below.
# @shared_task(autoretry_for=(Exception, ),
#              retry_kwargs={'max_retries': 1})
@shared_task
def download(url, opts=None):
    opts = opts or {}

    # TODO: Will be fixed that opts value is missing if happened retris,
    #       then url value converts as outfile
    outfile = opts.pop('outfile', _md5(url))
    is_download = opts.pop('download', True)

    default_opts = {
        'writethumbnail': True,
        'hls_prefer_native': True,
        'outtmpl': f'/tmp/%(id)s-----{outfile}.%(ext)s',
        'progress_hooks': [lambda d: store.set(outfile, d)]
    }

    with youtube_dl.YoutubeDL({**opts, **default_opts}) as ydl:
        try:
            result = _one(ydl.extract_info(url, download=is_download))
        except youtube_dl.utils.DownloadError as err:
            # TODO: remove file
            logger.error('Failure Download: %s, %r', url, err)
            raise

    outtmpl = default_opts['outtmpl'] % result
    buf = store.get(outfile)
    if buf and 'filename' in buf:
        outtmpl = buf['filename']

    filename = '/tmp/{}'.format(outtmpl.split('-----')[-1])

    if is_download and client.is_movie(outtmpl):
        # Upload video and image
        client.cheaper().upfile(filename, outtmpl)

    result.update({'outfile': filename})
    return result
