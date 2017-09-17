import os
import urllib
import mimetypes

from django.conf import settings

from minio import (
    Minio,
    policy,
    error
)

from core import error as core_error


def _client(host):
    return Minio(
        urllib.parse.urlparse(host).netloc,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )


class MC:
    def __init__(self, node, bucket=None):
        self.node = node
        self._mc = _client(node.host)
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
