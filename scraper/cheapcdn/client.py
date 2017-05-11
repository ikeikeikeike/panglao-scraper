import os
import random

from django.conf import settings

from minio import (
    Minio,
    policy,
    error
)

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


def minio_client(host=None):
    return Minio(
        host,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )


class CheapCDN:
    def __init__(self):
        self._mcs = self.load()

    def load(self):
        mcs = []
        for node in models.Node.objects.filter(alive=True):
            #  node.free =
            mcs.append(Mc(node))
        return mcs

    def choice(self):
        mcs, weights = [], []
        for mc in self._mcs:
            mcs.append(mc)
            weights.append(mc.free)

        k = random.choices(mcs, weights=weights, k=1)
        return k and k[0]

    def mc(self, node):
        mc = [mc for mc in self._mcs if mc.node.id == node.id]
        return mc and mc[0]

    def upfile(self, filename):
        key = os.path.basename(filename)
        obj, new = models.Object.objects.get_or_create(key=key)

        if not new:
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
        self._mc = minio_client(node.host)
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
        key = os.path.basename(filename)

        self._mc.put_object(self._bucket, key, f, size)
