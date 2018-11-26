"""
WSGI config for cathapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

python_home = '/usr/local/venvs/cathapi-prod'
activate_this = python_home + '/bin/activate_this.py'
exec(open(activate_this).read())

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cathapi.settings")

application = get_wsgi_application()
