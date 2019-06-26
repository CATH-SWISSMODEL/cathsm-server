"""Setting for production environment"""

from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'cathapi',
        # 'USER': 'cathapiuser',
        # 'HOST': 'localhost',
        # 'PORT': 5432,
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
