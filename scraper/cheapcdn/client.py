import os

from django.conf import settings

from minio import (
    Minio,
    policy,
    error
)

from core import error as core_error


def default_client():
    return Minio(
        settings.MINIO_HOST,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )


class CheapCDN:
    def __init__(self, bucket=None, client=None):
        self._bucket = bucket or settings.MINIO_BUCKET
        self._mc = client or default_client()

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

        with core_error.ignore(error.ResponseError):
            self._mc.put_object(self._bucket, filename, f, size)
