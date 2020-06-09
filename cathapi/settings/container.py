"""Setting for development environment"""

from decouple import config

from .base import *

# Bend the broker to the redis container
CELERY_BROKER_URL = 'redis://cathapi-redis:6379'
CELERY_RESULT_BACKEND = 'redis://cathapi-redis:6379'

# These settings make sure any tasks run in testing 
# are run locally with the 'test' database
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

IS_CELERY = config('I_AM_CELERY', default=False, cast=bool)

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('POSTGRES_DB', default='cathapi', cast=str),
        'USER': config('DJANGO_DB_USR', default='cathapiuser', cast=str),
        'PASSWORD': config('DJANGO_DB_CLR_PW', cast=str),
        'HOST': config('PG_HOST', default='postgres', cast=str),
        'PORT': config('PG_PORT', default=5432, cast=int),
    }
 }

if not IS_CELERY:
  # Bend the Django cache to use the redis container
  CACHES["default"]["LOCATION"] = "redis://cathapi-redis:6379/1"

# These settings are only relevant for Django instances
  STATICFILES_DIRS = [
      os.path.join('static/'),
  ]

  STATIC_ROOT = '/static'
