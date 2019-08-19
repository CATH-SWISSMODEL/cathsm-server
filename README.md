
# CATH-SM Server

[![Build Status](https://travis-ci.com/CATH-SWISSMODEL/cath-swissmodel-api.svg?branch=master)](https://travis-ci.com/CATH-SWISSMODEL/cath-server)

This repository contains scripts and libraries for running the backend Django server
required for the CATH-SM (CATH/SWISS-MODEL) protein sequence modelling pipeline.

## Overview

* Install dependencies
* Create Python virtual environment
* Start up Celery worker
* Start up Django server

## Dependencies

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

## Python environment

### Install virtual environment

```
python3 -m venv venv
. venv/bin/activate
pip install -e .
```

### Run tests

```
pytest
```

### Create a unique secret key

```sh
cd cathsm-server && source venv/bin/activate
date | md5sum > secret_key.txt
```

### Update the local database

```sh
cd cathsm-server && source venv/bin/activate
python3 manage.py makemigrations
python3 manage.py migrate
```

## Start a Celery worker (to process jobs)

```sh
cd cathsm-server && source venv/bin/activate
CATHAPI_DEBUG=1 celery -A cathapi worker
```

## Start a local API server

```sh
cd cathsm-server && source venv/bin/activate
CATHAPI_DEBUG=1 python3 manage.py runserver
```

An instance of **API1** should now be available at:

http://127.0.0.1:8000/
