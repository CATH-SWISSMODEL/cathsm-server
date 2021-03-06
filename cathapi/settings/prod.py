"""Setting for production environment"""

from decouple import config

from .base import *

# turn off debug

DEBUG = False

# use PostgreSQL in production

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('PG_NAME', default='cathapi', cast=str),
        'USER': config('PG_USER', default='cathapiuser', cast=str),
        'PASSWORD': config('PG_PASSWORD', cast=str),
        'HOST': config('PG_HOST', default='localhost', cast=str),
        'PORT': config('PG_PORT', default=5432, cast=int),
    }
}

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://cathapi-redis:6379')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://cathapi-redis:6379')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://cathapi-redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "cathapi"
    }
}

# need to set up mailgun

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.mailgun.org'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'mytestuser'
# EMAIL_HOST_PASSWORD = 'mytestpassword'
# EMAIL_USE_TLS = True
