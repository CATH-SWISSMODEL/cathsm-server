"""Setting for development environment"""

from .base import *

DEBUG = True

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
