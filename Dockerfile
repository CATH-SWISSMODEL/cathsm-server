FROM python:3

# https://semaphoreci.com/community/tutorials/dockerizing-a-python-django-web-application

ARG CATHPY_VERSION=v0.0.1
ARG CATHPY_SRC=git@github.com:UCL/cathpy.git
ARG CODE_SRC=git@github.com:CATH-SWISSMODEL/cath-swissmodel-api.git
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /code /deps
WORKDIR /code
ADD requirements-to-freeze.txt /code
ADD repo-key /
RUN chmod 600 /repo-key \
    && echo "IdentityFile /repo-key" >> /etc/ssh/ssh_config \
    && echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config \
    && git clone --branch ${CATHPY_VERSION} ${CATHPY_SRC} /deps/cathpy
RUN git clone ${CODE_SRC} .
RUN pip install -e /deps/cathpy
RUN pip install -r requirements-to-freeze.txt

