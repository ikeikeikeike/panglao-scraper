import hashlib
from django.core.cache import caches

store = caches['progress']


def _key(key):
    return hashlib.md5(key.encode()).hexdigest()


def set(key, value):
    return store.set(_key(key), value)


def get(key):
    return store.get(_key(key))
