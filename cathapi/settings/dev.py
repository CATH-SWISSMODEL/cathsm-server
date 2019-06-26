"""Setting for development environment"""

from .base import *

DEBUG = True

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

# These settings make sure any tasks run in testing 
# are run locally with the 'test' database
CELERY_ALWAYS_EAGER = True
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS += [
    #    'debug_toolbar',
]

#MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
