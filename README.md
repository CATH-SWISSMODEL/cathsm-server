
# CATH-SM Server

[![Build Status](https://travis-ci.com/CATH-SWISSMODEL/cath-swissmodel-api.svg?branch=master)](https://travis-ci.com/CATH-SWISSMODEL/cath-server)

This repository contains scripts and libraries for running the backend Django server
required for the CATH-SM (CATH/SWISS-MODEL) protein sequence modelling pipeline.

## Overview

This code provides a Django server that manages a protein structural modelling pipeline
via asynchronous web jobs to the CATH and SWISS-MODEL APIs. Local computation is carried
out by a [Celery](http://www.celeryproject.org/) worker (with [Redis](https://redis.io/) 
used as the cache/message broker).

A public deployment can be found here:

https://api01.cathdb.info

## Local Install

Overview:

* Install dependencies
* Setup Python environment
* Start up Celery worker
* Start up Django server

### Install Dependencies

Redis is used as a cache/message broker:

```sh
# Ubuntu
sudo apt-get install redis

# CentOS / RedHat
sudo yum install redis
```

Run the service in the background.

```sh
sudo systemctl enable redis
sudo systemctl start redis
```

Note: PostgreSQL is used as the deployment database (which will also need to be installed and configured), however the development database uses the built-in SQLite.

### Setup Python environment

#### Install virtual environment

```bash
python3 -m venv venv
. venv/bin/activate
pip install -e .
```

#### Run tests

```bash
python3 -m pytest
```

#### Update the local database

```bash
cd cathsm-server && source venv/bin/activate
python3 manage.py makemigrations
python3 manage.py migrate
```

### Start Celery worker (to process jobs)

```sh
cd cathsm-server && source venv/bin/activate
CATHAPI_DEBUG=1 celery -A cathapi worker
```

### Start server

```sh
cd cathsm-server && source venv/bin/activate
CATHAPI_DEBUG=1 python3 manage.py runserver
```

An instance of `cathsm-server` should now be available at:

http://127.0.0.1:8000/
