
"""
Run tasks in the background with Celery
"""
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# DJANGO_SETTINGS_MODULE=cathapi.settings.dev celery -A cathapi -l info
if 'CATHAPI_DEBUG' in os.environ:
    django_settings = 'cathapi.settings.dev'
else:
    django_settings = 'cathapi.settings.prod'

print("Running Django server with: {}".format(django_settings))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", django_settings)

app = Celery('cathapi')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
