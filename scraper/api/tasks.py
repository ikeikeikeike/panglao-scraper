from __future__ import absolute_import, unicode_literals
import time
import hashlib
import logging
from urllib import error as uerror
from urllib.parse import urlsplit

from django.conf import settings
from django.core.cache import caches

from celery import shared_task

import youtube_dl

from cheapcdn import (
    conv,
    client
)

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
    elif 'nicovideo.jp' in domain:
        return {'username': settings.NICO_USER,
                'password': settings.NICO_PASS}
    return {}


def info(url, opts=None):
    opts = {**_respond_opts(url), **(opts or {})}

    with youtube_dl.YoutubeDL(opts) as ydl:
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
#
# TODO: Will be fixed that opts value(outfile) is missing if happened retris,
#       then url value converts as outfile
#
# @shared_task(autoretry_for=(Exception, ),
#              retry_kwargs={'max_retries': 1})
@shared_task
def download(url, opts=None):
    logger.info('Start download: %s', url)

    opts = opts or {}

    dl = opts.pop('download', True)
    outfile = opts.pop('outfile', _md5(url))

    dlopts = {**_respond_opts(url), **{
        'writethumbnail': True,
        'hls_prefer_native': True,
        'outtmpl': f'/tmp/%(id)s-----{outfile}.%(ext)s',
        'progress_hooks': [lambda d: store.set(outfile, d)]
        #  'progress_hooks': [lambda d: store.set(outfile, d); raise]
    }}

    with youtube_dl.YoutubeDL({**opts, **dlopts}) as ydl:
        result = retry_manually(ydl, url, dl, outfile)

    outtmpl = dlopts['outtmpl'] % result
    # buf = store.get(outfile)
    # if buf and 'filename' in buf:
    #     outtmpl = buf['filename']

    filename = '/tmp/{}'.format(outtmpl.split('-----')[-1])

    if dl and conv.Media(outtmpl).is_movie():
        # Upload video and image
        logger.info('Start upload: %s', url)
        client.CheapCDN().upfile(filename, outtmpl)
        logger.info('Finish upload: %s', url)

    result.update({'outfile': filename})
    return result


def retry_manually(ydl, url, dl, outfile, retry=1):
    try:
        return _one(ydl.extract_info(url, download=dl))
    except youtube_dl.utils.DownloadError as err:  # except Exception as err:
        # TODO: remove file
        #
        logger.warning('retry=%d failure download: %s, %r', retry, url, err)
        if retry >= 5:
            _crap = {
                '_eta_str': '--:--:--',
                '_percent_str': '  0.0%',
                '_speed_str': 'Unknown speed',
                '_total_bytes_estimate_str': '0GiB',
                'downloaded_bytes': 0,
                'elapsed': 0,
                'eta': 0,
                'filename': 'mp4',
                'speed': 0,
                'status': 'crap',
                'tmpfilename': 'mp4.part',
                'total_bytes_estimate': 0
            }
            store.set(outfile, _crap)
            raise

        time.sleep(30)
        return retry_manually(ydl, url, download, outfile, retry + 1)
