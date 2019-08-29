FROM postgres:11.4-alpine

# For more information check https://hub.docker.com/_/postgres and
# https://docs.docker.com/samples/library/postgres/

COPY 10-create-django-user.sql /docker-entrypoint-initdb.d/

COPY postgresql.conf /

USER postgres
