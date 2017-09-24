import os
import time
import logging
import mimetypes
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

import boto3
import botocore
import tldextract

from core import error as core_error

logger = logging.getLogger(__name__)

_timeago = 2.5  # period time of deletion
_maxsize = 1099511627776  # 1TB

session = boto3.session.Session()


def _client(host):
    return session.client(
        's3',
        region_name=tldextract.extract(host).subdomain,
        endpoint_url=host,
        aws_access_key_id=settings.DO_ACCESS_KEY,
        aws_secret_access_key=settings.DO_SECRET_KEY,
        config=botocore.client.Config(s3={'addressing_style': 'virtual'})
    )


class DO:
    def __init__(self, node, bucket=None):
        self.node = node
        self._mc = _client(node.host)
        self._bucket = bucket or settings.DO_BUCKET

        self.prepare_bucket()

    def exists_bucket(self, bucket):
        try:
            self._mc.head_bucket(Bucket=bucket)
        except botocore.exceptions.ClientError:
            return False
        return True

    # now unuse this method
    def bucket_size(self, bucket):
        r = self._mc.list_objects_v2(Bucket=bucket, MaxKeys=999999)
        return sum(i['Size'] for i in r.get('Contents', [])) or 0

    def prepare_bucket(self):
        # make bucket
        if not self.exists_bucket(self._bucket):
            with core_error.ignore(Exception):
                self._mc.create_bucket(Bucket=self._bucket)

        # calclate bucket size and delete old objects
        usedsize = 0
        timeago = timezone.now() - timedelta(days=_timeago)

        r = self._mc.list_objects_v2(Bucket=self._bucket, MaxKeys=999999)
        for i in r.get('Contents', []):
            if i['LastModified'] < timeago:
                self._mc.delete_object(Bucket=self._bucket, Key=i['Key'])
            else:
                usedsize += i['Size']

        self.node.free = _maxsize - usedsize
        self.node.save()

    def upfile(self, filename):
        mime, _ = mimetypes.guess_type(filename)  # TODO: Will be specific extractor

        def fun():
            return self._mc.put_object(
                ACL='public-read',
                Key=os.path.basename(filename),
                Body=open(filename, 'rb'),
                Bucket=self._bucket,
                ContentLength=os.stat(filename).st_size,
                ContentType=mime or 'video/mp4'
            )
        etag = retry_manually(fun)
        return etag

    def rmfile(self, filename):
        key = os.path.basename(filename)
        return self._mc.delete_object(Bucket=self._bucket, Key=key)


def retry_manually(fun, retry=1):
    try:
        return fun()
    except botocore.exceptions.ClientError as err:
        logger.warning('retry=%d upfile: %r', retry, err)
        if retry >= 10:
            logger.error('upfile came max retries: %r', err)
            raise

        time.sleep(5)
        return retry_manually(fun, retry + 1)
