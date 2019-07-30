"""Setting for development environment"""

from decouple import config

from .base import *

# Bend the broker to the redis container
BROKER_URL = 'redis://cathapi-redis:6379'
CELERY_RESULT_BACKEND = 'redis://cathapi-redis:6379'

# These settings make sure any tasks run in testing 
# are run locally with the 'test' database
CELERY_ALWAYS_EAGER = True
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

IS_CELERY = config('I_AM_CELERY', default=False, cast=bool)

if not IS_CELERY:
  # These settings are only relevant for Django instances
  DEBUG = True

  # Bend the Django cache to use the redis container
  CACHES["default"]["LOCATION"] = "redis://cathapi-redis:6379/1"

  '''
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql_psycopg2',
          'NAME': config('PG_NAME', default='cathapi', cast=str),
          'USER': config('PG_USER', default='cathapiuser', cast=str),
          'PASSWORD': config('POSTGRES_PASSWORD', cast=str),
          'HOST': config('PG_HOST', default='postgres', cast=str),
          'PORT': config('PG_PORT', default=5432, cast=int),
      }
   }
  '''

  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.sqlite3',
          'NAME': os.path.join('/cathapi-data', 'db.sqlite3'),
      }
  }

  INSTALLED_APPS += [
      #    'debug_toolbar',
  ]

  STATICFILES_DIRS = [
      os.path.join('static/'),
  ]

  STATIC_ROOT = '/static'

  #MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
