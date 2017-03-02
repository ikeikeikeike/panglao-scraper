import random
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import caches

import requests
import eventlet

from requests import adapters

any_cache = caches['tmp_anything']


def rq(headers=None):
    retries = adapters.HTTPAdapter(max_retries=40)
    ua = random.choice(settings.USER_AGENTS)

    s = requests.Session()

    s.headers['User-Agent'] = ua
    s.headers.update(headers or {})

    s.mount('http://', retries)
    s.mount('https://', retries)
    return s


def json(uri, headers=None, auth=None):
    uri = _prepare(uri)
    js = any_cache.get(uri, version=3)

    if not js:
        r = request(uri, headers, auth)
        if r and r.ok:
            js = r.json()
            any_cache.set(uri, js, version=3)

    return js


def html(uri, headers=None, auth=None):
    uri = _prepare(uri)
    content = any_cache.get(uri, version=4)

    if not content:
        r = request(uri, headers, auth)
        if r and r.ok:
            content = r.content
            any_cache.set(uri, content, version=4)

    return content


def text(uri, headers=None, auth=None):
    uri = _prepare(uri)
    content = any_cache.get(uri, version=5)

    if not content:
        r = request(uri, headers, auth)
        if r and r.ok:
            content = r.text
            any_cache.set(uri, content, version=5)

    return content


def request(uri, headers=None, auth=None):
    try:
        with eventlet.Timeout(10):
            r = rq(headers or {}).get(uri, verify=False, auth=auth)
    except (
        eventlet.timeout.Timeout,
        requests.exceptions.ConnectionError,
    ):
        return None
    return r


def _prepare(url):
    u = urlparse(url)

    if u.scheme:
        return url

    u = u._replace(scheme='http')
    if request(u.geturl()):
        return u.geturl()

    u = u._replace(scheme='https')
    return u.geturl()
