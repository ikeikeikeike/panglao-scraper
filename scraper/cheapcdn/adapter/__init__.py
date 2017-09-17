from . import minio
from . import digitalocean


def get_client(node):
    if node.provider == 'digitalocean':
        return digitalocean.DO(node)
    elif node.provider == 'minio':
        return minio.MC(node)
    return minio.MC(node)
