import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'j!olsl1$0h!k4hqsx@7d@2iu9cgtv77+d90$insjcco7#l38a-'

DEBUG = True
ALLOWED_HOSTS = ['*']

# Configures manually
ENVIRONMENT = ''

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'api',
    'cheapcdn',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scraper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scraper.wsgi.application'

DATABASE_ROUTERS = ['scraper.dbrouter.DBRouter']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default-location'
    },
    'progress': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'progress-location'
    },
    "tmp_image": {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tmpimage-location'

    },
    "tmp_anything": {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tmpanything-location'
    },
    'lock_in_task': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'lockintask-location'
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

CELERY_BROKER_URL = 'redis://localhost:6379/11'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/11'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

MINIO_BUCKET = ''
MINIO_ACCESS_KEY = ''
MINIO_SECRET_KEY = ''

DO_BUCKET = ''
DO_ACCESS_KEY = ''
DO_SECRET_KEY = ''

DO_TOKEN = ''
DO_SSH_KEYS = ''
DO_OBJECT_IMAGE = ''

# logging
LOGGING_PREFIX = 'scraper'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'verbose': {
            '()': 'colorlog.ColoredFormatter',
            'format': ('%(log_color)s[%(levelname)s]'
                       '[in %(pathname)s:%(lineno)d]'
                       '%(asctime)s %(process)d %(thread)d '
                       '%(module)s: %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'log_colors': {
                'DEBUG': 'bold_black',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
        'sql': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(cyan)s[SQL] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'syslog_verbose': {
            'format': ('{}:[%(levelname)s] [in %(pathname)s:%(lineno)d] '
                       '%(asctime)s %(process)d %(thread)d '
                       '%(module)s: %(message)s'.format(LOGGING_PREFIX)),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'sql': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'sql'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'sentry': {
            'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'environment': ENVIRONMENT},
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'address': '/var/run/syslog' if sys.platform == 'darwin' else '/dev/log',
            'formatter': 'syslog_verbose',
            #  'filters': ['require_debug_false'],
            #  'facility': 'local1',
        },
    },
    'loggers': {
        '': {
            'handlers': ['syslog', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.db.backends': {
            'handlers': ['sql'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # 'django': {
        #     'handlers': ['syslog', 'console'],
        #     'level': 'DEBUG',
        #     'propagate': True
        # },
        # LOGGING_PREFIX: {
        #     'handlers': ['syslog', 'console'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        # 'raven': {
        #     'level': 'DEBUG',
        #     'handlers': ['sentry'],
        #     'propagate': False,
        # },
        # 'sentry.errors': {
        #     'level': 'DEBUG',
        #     'handlers': ['sentry'],
        #     'propagate': False,
        # },
    }
}
