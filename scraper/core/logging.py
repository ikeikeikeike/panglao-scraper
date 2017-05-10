import logging
from django.conf import settings


getLogger = lambda name: logging.getLogger('%s.%s' % (settings.LOGGING_PREFIX, name))
