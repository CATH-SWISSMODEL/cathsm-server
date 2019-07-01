"""Setting for production environment"""

from decouple import config

from .base import *

DEBUG = False

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

ALLOWED_HOSTS = ['.cathdb.info', 'orengoapi01']

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient"
#         },
#         "KEY_PREFIX": "cathapi"
#     }
# }

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'mytestuser'
EMAIL_HOST_PASSWORD = 'mytestpassword'
EMAIL_USE_TLS = True
