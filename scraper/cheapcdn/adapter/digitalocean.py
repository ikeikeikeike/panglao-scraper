import os
import mimetypes

from django.conf import settings

import boto3
import botocore

from core import error as core_error

_maxsize = 1099511627776  # 1TB

session = boto3.session.Session()


def _client(host='https://nyc3.digitaloceanspaces.com'):
    return session.client(
        's3',
        region_name='nyc3',
        endpoint_url=host,
        aws_access_key_id=settings.DO_ACCESS_KEY,
        aws_secret_access_key=settings.DO_SECRET_KEY,
        config=botocore.client.Config(s3={'addressing_style': 'virtual'})
    )


class DO:
    def __init__(self, node, bucket=None):
        self.node = node
        self._mc = _client()
        self._bucket = bucket or settings.DO_BUCKET

        self.prepare_bucket()

    def exists_bucket(self, bucket):
        try:
            self._mc.head_bucket(Bucket=bucket)
        except botocore.exceptions.ClientError:
            return False
        return True

    def bucket_size(self, bucket):
        r = self._mc.list_objects_v2(Bucket=bucket)
        return sum(i['Size'] for i in r['Contents'])

    def prepare_bucket(self):
        if not self.exists_bucket(self._bucket):
            with core_error.ignore(Exception):
                self._mc.create_bucket(Bucket=self._bucket)

        self.node.free = _maxsize - self.bucket_size(self._bucket)
        self.node.save()

    def upfile(self, filename):
        mime, _ = mimetypes.guess_type(filename)  # TODO: Will be specific extractor

        etag = self._mc.put_object(
            Key=os.path.basename(filename),
            Body=open(filename, 'rb'),
            Bucket=self._bucket,
            ContentLength=os.stat(filename).st_size,
            ContentType=mime or 'video/mp4'
        )
        return etag

    def rmfile(self, filename):
        key = os.path.basename(filename)
        return self._mc.delete_object(Bucket=self._bucket, Key=key)