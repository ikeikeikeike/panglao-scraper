from __future__ import absolute_import, unicode_literals
import hashlib
import logging
from urllib import error as uerror
from urllib.parse import urlsplit

from django.core.cache import caches

from celery import shared_task
from celery.utils.log import get_task_logger

import youtube_dl

#  from core import extractor
from cheapcdn import (
    conv,
    client
)

clogger = get_task_logger(__name__)
logger = logging.getLogger(__name__)
store = caches['progress']


def _md5(text):
    return hashlib.md5(text.encode()).hexdigest()


def _one(result):
    entry = result.pop('entries', [{}])[0]
    return {**result, **entry}


def _respond_opts(url):
    domain = "{0.netloc}".format(urlsplit(url))
    if 'youtube.com' in domain:
        return {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'}
    return {}


def info(url, opts=None):
    with youtube_dl.YoutubeDL(opts or {}) as ydl:
        try:
            return _one(ydl.extract_info(url, download=False))
        except youtube_dl.utils.DownloadError as err:
            # TODO: remove file
            logger.error('Failure info: %s, %r', url, err)

            _, obj, _ = err.exc_info
            if isinstance(obj, uerror.HTTPError):
                return obj.code
            return 0


# TODO: count-up zero and comment in if fixed TODO below.
# @shared_task(autoretry_for=(Exception, ),
#              retry_kwargs={'max_retries': 1})
@shared_task
def download(url, opts=None):
    logger.info('Start download: %s', url)

    opts = opts or {}

    # TODO: Will be fixed that opts value is missing if happened retris,
    #       then url value converts as outfile
    outfile = opts.pop('outfile', _md5(url))
    is_download = opts.pop('download', True)

    default_opts = {**_respond_opts(url), **{
        'writethumbnail': True,
        'hls_prefer_native': True,
        'outtmpl': f'/tmp/%(id)s-----{outfile}.%(ext)s',
        'progress_hooks': [lambda d: store.set(outfile, d)]
    }}

    with youtube_dl.YoutubeDL({**opts, **default_opts}) as ydl:
        try:
            result = _one(ydl.extract_info(url, download=is_download))
        except youtube_dl.utils.DownloadError as err:
            # TODO: remove file
            logger.error('Failure download: %s, %r', url, err)
            raise

    outtmpl = default_opts['outtmpl'] % result
    # buf = store.get(outfile)
    # if buf and 'filename' in buf:
    #     outtmpl = buf['filename']

    filename = '/tmp/{}'.format(outtmpl.split('-----')[-1])

    if is_download and conv.Media(outtmpl).is_movie():
        # Upload video and image
        clogger.warning('Start upload: %s', url)
        client.CheapCDN().upfile(filename, outtmpl)
        clogger.warning('Finish upload: %s', url)

    result.update({'outfile': filename})
    return result
