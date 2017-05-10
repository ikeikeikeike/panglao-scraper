from contextlib import contextmanager

from core import logging

logger = logging.getLogger(__name__)


@contextmanager
def ignore(*exc):
    try:
        yield
    except exc as err:
        logger.error(err)
