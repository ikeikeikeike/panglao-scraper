import os
import glob
import shutil
import random
import mimetypes

from django.conf import settings
from django.db import transaction

import netifaces as ni
from urllib3 import exceptions as uexcepts
from minio import (
    Minio,
    policy,
    error
)

from core import (
    logging,
    error as core_error
)

from . import (
    conv,
    models
)


logger = logging.getLogger(__name__)

_maxsize = 5368709120  # byte(5GB)


class state(type):
    _instance = None
    _interval = 0

    def __call__(cls, *args, **kwargs):
        cls._interval += 1

        if cls._instance is None or cls._interval >= 5:
            cls._instance = super(state, cls).__call__(*args, **kwargs)
            cls._interval = 0

        return cls._instance


class CheapCDN(metaclass=state):

    def __init__(self):
        self._mcs = self.load()

    def load(self):
        objects = models.Node.objects

        with transaction.atomic():
            node, _ = objects.get_or_create(host=extract_host())
        node.free = extract_free()
        node.save()

        mcs = []
        for node in objects.filter(alive=True):
            try:
                mcs.append(Mc(node))
            except uexcepts.MaxRetryError:
                pass
        return mcs

    def choice(self):
        mcs, weights = [], []
        for mc in filter(lambda x: x.node.choiceable, self._mcs):
            if len(self._mcs) == 1:
                mcs.append(mc)
                weights.append(mc.node.free)
            elif mc.node.free > _maxsize:
                mcs.append(mc)
                weights.append(mc.node.free)

        k = random.choices(mcs, weights=weights, k=1)
        return k and k[0]

    def mc(self, node):
        mc = [mc for mc in self._mcs if mc.node.id == node.id]
        return mc and mc[0]

    def nodeinfo(self):
        q = models.Node.objects.all()
        return q.values('host', 'free', 'alive', 'choiceable')

    def is_abledisk(self):
        nodes = filter(lambda x: x['choiceable'], self.nodeinfo())

        ngsize = _maxsize + _maxsize
        return any(map(lambda x: x['free'] > ngsize, nodes))

    def findprefix(self, filename):
        # XXX: make sure minio object if sometime result goes wrong below.
        name, _ = os.path.splitext(filename)
        q = models.Object.objects.filter(name__startswith=name)
        return q.values_list('name', flat=True)

    def rmfile(self, filename):
        self._rmfile(filename)
        for rmfile in conv.Media(filename).filenames():
            self._rmfile(rmfile)

    def _rmfile(self, filename):
        name = os.path.basename(filename)
        obj = models.Object.objects.get(name=name)

        mc = self.mc(obj.node)
        mc.rmfile(filename)
        obj.delete()

    def upfile(self, filename, outtmpl=None):
        if outtmpl:
            _rename(outtmpl, filename)

        if not self._upfile(filename):
            return

        m = conv.Media(filename)
        m.conv_all()

        for upfile in m.filenames():
            self._upfile(upfile)

        os.remove(filename)
        m.cleanup()

    def _upfile(self, filename):
        name = os.path.basename(filename)
        with transaction.atomic():
            obj, _ = models.Object.objects.get_or_create(name=name)

        if obj.node:
            mc = self.mc(obj.node)
        else:
            mc = self.choice()
            obj.node = mc.node
            obj.save()

        try:
            return mc.upfile(filename)
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
        f, size = open(filename, 'rb'), os.stat(filename).st_size
        name = os.path.basename(filename)
        mime, _ = mimetypes.guess_type(filename)  # TODO: Will be specific extractor

        etag = self._mc.put_object(self._bucket, name, f, size,
                                   content_type=mime or 'video/mp4')
        return etag

    def rmfile(self, filename):
        name = os.path.basename(filename)
        return self._mc.remove_object(self._bucket, name)


def _rename(outtmpl, filename):
    shutil.move(outtmpl, filename)

    obase, _ = os.path.splitext(outtmpl)
    if os.path.exists(f'{obase}.jpg'):
        fbase, _ = os.path.splitext(filename)
        shutil.move(f'{obase}.jpg', f'{fbase}.jpg')


def extract_host():
    """ workaround until release this
        https://github.com/minio/mc/pull/2036
    """
    try:
        host = ni.ifaddresses('eth1')[2][0]['addr']
    except ValueError:
        host = '127.0.0.1'

    return f'{host}:9091'


def extract_free():
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
