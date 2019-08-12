#!/bin/bash

function redis_ready(){
python3 << END 
import sys
import os
import redis
if 'CATHAPI_DEBUG' in os.environ:
    if os.environ['CATHAPI_DEBUG'].upper() == 'CONTAINER':
        import cathapi.settings.container as config
    else:
        import cathapi.settings.dev as config
else:
    import cathapi.settings.prod as config
for url in [config.CACHES["default"]["LOCATION"], config.BROKER_URL,
            config.CELERY_RESULT_BACKEND]:
    try:
        rds = redis.from_url(url)
        rds.ping()
    except redis.exceptions.RedisError:
        sys.stderr.write("Redis host '%s' not ready, try again.\n" % url)
        sys.exit(1)
    except:
        raise
        sys.exit(2)
sys.exit(0)
END
}

function postgres_ready(){
python3 << END
import sys
import cathapi.wsgi
from django.db import connections
from django.db.utils import OperationalError
db_conn = connections['default']
try:
    db_conn.cursor()
except OperationalError:
    sys.exit(1)
except:
  raise
  sys.exit(2)
sys.exit(0)
END
}

# exit immediately on commands with a non-zero exit status.
set -e

# wait for Redis
>&2 echo "Wait for Redis"
until redis_ready; do
    >&2 echo "Redis is not ready yet - sleep 1s"
    sleep 1
done
>&2 echo "Redis up and running"

# wait for the database
>&2 echo "Wait for database"
until postgres_ready; do
    >&2 echo "Database is not ready yet - sleep 1s"
    sleep 1
done
>&2 echo "Database up and running"

# Make sure the database is set up
>&2 echo "Assure database is set up with tables"
python3 manage.py makemigrations
python3 manage.py migrate

# Install static files
python3 manage.py collectstatic --noinput

# create root account for Django admin page
>&2 echo "Create superuser for the database"
python3 manage.py shell << END 
from django.contrib.auth.models import User
try:
    User.objects.get(username='admin')
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'ad@m.in', 'admin')
except Exception as dexc:
    if str(dexc) == 'UNIQUE constraint failed: auth_user.username':
        pass
except:
    raise
END

exec "$@"
