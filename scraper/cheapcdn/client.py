import os
import glob
import shutil
import random
import mimetypes
import subprocess

from django.conf import settings

from minio import (
    Minio,
    policy,
    error
)

import netifaces as ni

from core import (
    logging,
    error as core_error
)

from . import models


logger = logging.getLogger(__name__)


_cheapcdn = None
_interval = range(0, 50)


def cheaper():
    global _cheapcdn
    if _cheapcdn is None or random.choice(_interval) == 0:
        cheapcdn = CheapCDN()

    return cheapcdn


class CheapCDN:
    def __init__(self):
        self._mcs = self.load()

    def load(self):
        objects = models.Node.objects

        node, _ = objects.get_or_create(host=_extract_host())
        node.free = _extract_free()
        node.save()

        mcs = []
        for node in objects.filter(alive=True):
            mcs.append(Mc(node))
        return mcs

    def choice(self):
        mcs, weights = [], []
        for mc in self._mcs:
            mcs.append(mc)
            weights.append(mc.node.free)

        k = random.choices(mcs, weights=weights, k=1)
        return k and k[0]

    def mc(self, node):
        mc = [mc for mc in self._mcs if mc.node.id == node.id]
        return mc and mc[0]

    def upfile(self, filename):
        name = os.path.basename(filename)
        obj, _ = models.Object.objects.get_or_create(name=name)

        if obj.node:
            mc = self.mc(obj.node)
        else:
            mc = self.choice()
            obj.node = mc.node
            obj.save()

        try:
            mc.upfile(filename)
        except error.ResponseError as err:
            logger.error('%s with %s', err, filename)
        except AttributeError:
            logger.error('mc is nothing with %s', filename)


class Mc:
    def __init__(self, node, bucket=None):
        self.node = node
        self._mc = _minio_client(node.host)
        self._bucket = bucket or settings.MINIO_BUCKET

        self.prepare_bucket()

    def prepare_bucket(self):
        if self._mc.bucket_exists(self._bucket):
            return

        with core_error.ignore(error.ResponseError):
            self._mc.make_bucket(self._bucket)

        self._mc.set_bucket_policy(
            self._bucket, '*', policy.Policy.READ_ONLY
        )

    def upfile(self, filename):
        if not self._upfile(filename):
            return

        base, _ = os.path.splitext(filename)

        if not os.path.exists(f'{base}.jpg'):
            _generate_jpg(filename)

        self._upfile(f'{base}.jpg')

    def _upfile(self, filename):
        f, size = open(filename, 'rb'), os.stat(filename).st_size
        name = os.path.basename(filename)
        mime, _ = mimetypes.guess_type(filename)  # TODO: Will be specific extractor

        etag = self._mc.put_object(self._bucket, name, f, size,
                                   content_type=mime or 'video/mp4')
        os.remove(filename)  # XXX: Remove file
        return etag


def _generate_jpg(filename):
    dest, _ = os.path.splitext(filename)
    cmd = [
        'ffmpeg',
        '-ss', '60',
        '-i', filename,
        '-qscale:v', '0',
        '-vframes', '1',
        f'{dest}.jpg'
    ]
    return subprocess.run(cmd)


def _extract_host():
    """ workaround until release this
        https://github.com/minio/mc/pull/2036
    """
    try:
        host = ni.ifaddresses('eth1')[2][0]['addr']
    except ValueError:
        host = '127.0.0.1'

    return f'{host}:9091'


def _extract_free():
    """ workaround until release
        this https://github.com/minio/mc/pull/2036
    """
    mnt = glob.glob('/mnt/object*')
    mnt = mnt[0] if mnt else ''

    try:
        return shutil.disk_usage(mnt).free
    except (FileNotFoundError, TypeError):
        return 1024


def _minio_client(host=None):
    return Minio(
        host,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )
