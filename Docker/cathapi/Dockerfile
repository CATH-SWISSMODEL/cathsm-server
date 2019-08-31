ARG CATHSMAPI_CODEBASE=fromlocal
FROM python:3.7.4-slim-buster as cath_sm_api_basis

# To build it outside of docker-compose, in the toplevel directory of the repository,
# run:
#
# $ docker build -f Docker/cathapi/Dockerfile -t cathapi .
#
# where
# - "-t cathapi" just defines a name/ tag
#
# By default, the images is created using a local checkout of the Git repo. To
# let Docker check out the repo for you during build time, start the build
# command using `--build-arg CATHSMAPI_CODEBASE=fromgitrepo`.
#
# Be aware: some (secret) environment variables are passed by an .env file
#           this is copied here from cathapi/Docker/cathapi/.env .

ENV SRC_DIR="/cathapi"

# Get API code inside the image - we can either use a local checkout of the
# Git repository by using CATHSMAPI_CODEBASE=fromlocal or check out the Git repo
# during build time by CATHSMAPI_CODEBASE=fromgitrepo. Due to the use of the
# "ONBUILD" instruction, copying files from the Docker build context OR
# checkout of the Git repo is ONLY executed on what ever
# "FROM build_${CATHSMAPI_CODEBASE}" calls. That is, if you want to build
# containers and just have this Dockerfile lying around in your home directory,
# no files from your hard drive will be copied inside the image.
FROM cath_sm_api_basis as build_fromlocal
ONBUILD RUN /bin/mkdir $SRC_DIR
ONBUILD COPY ./ $SRC_DIR

FROM cath_sm_api_basis as build_fromgitrepo
ONBUILD RUN apt-get update && \
            apt-get install -y --no-install-recommends \
            git && \
            /bin/rm -rf /var/lib/apt/lists/* && \
            /usr/bin/git clone https://github.com/bienchen/cath-swissmodel-api.git \
                               /tmp/cath-swissmodel-api.git && \
            if test -z "$CATHSMAPI_GITTAG"; then \
              cd /tmp/cath-swissmodel-api.git/cathapi && \
              git checkout $CATHSMAPI_GITTAG && \
              cd /; \
            fi && \
            /bin/mv /tmp/cath-swissmodel-api.git/cathapi $SRC_DIR && \
            /bin/rm -rf rm /tmp/cath-swissmodel-api.git && \
            apt-get purge -y --auto-remove git

FROM build_${CATHSMAPI_CODEBASE}

WORKDIR $SRC_DIR

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # +134MB by ncbi-blast+
    ncbi-blast+  \
    # +9MB by mafft
    mafft        \
    # +81MB gcc
    gcc          \
    libc-dev     \
    libpq5       \
    libpq-dev && \
    /bin/rm -rf /var/lib/apt/lists/* && \
# Install Python dependencies
    /usr/local/bin/pip install --no-cache-dir -r requirements.txt && \
# Clean up
    apt-get purge -y --auto-remove gcc libc-dev libpq-dev && \
    find /usr/local \( -type d -a -name test -o -name tests \) \
                   -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
                   -exec rm -rf '{}' \+

# Create the secret key
RUN /bin/date | /usr/bin/md5sum > secret_key.txt

# Run the tests
#RUN /usr/local/bin/pytest

COPY Docker/cathapi/entrypoint.sh $SRC_DIR

# Create dedicated user
RUN adduser --system --ingroup users cathapi && \
    # Create volume mountpoint for the (still sqlite) database
    /bin/mkdir /cathapi-data && \
    chown -R cathapi:users /cathapi-data && \
    # Create directory for static files
    /bin/mkdir /static && \
    chown -R cathapi:users /static && \
    # grant dedicated user access to code
    chown -R cathapi:users $SRC_DIR

USER cathapi:users

# The following lets Python write to STDOUT without buffering and prevents
# Python byte-compilation. We do not want *.pyc files generated at run-time,
# since those will vanish on container-restart. They would be newly created
# after every start of the container.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# LocalWords:  repo arg CATHSMAPI CODEBASE fromgitrepo fromlocal ONBUILD
