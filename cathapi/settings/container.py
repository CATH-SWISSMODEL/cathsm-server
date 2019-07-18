"""Setting for development environment"""

from .base import *

DEBUG = True

# Bend the Django cache to use the redis container
CACHES["default"]["LOCATION"] = "redis://cathapi-redis:6379/1"

# Bend the broker to the redis container
BROKER_URL = 'redis://cathapi-redis:6379'
CELERY_RESULT_BACKEND = 'redis://cathapi-redis:6379'

# These settings make sure any tasks run in testing 
# are run locally with the 'test' database
CELERY_ALWAYS_EAGER = True
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'


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
