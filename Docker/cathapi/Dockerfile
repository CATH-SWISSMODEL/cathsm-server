FROM python:3.7.3-slim-stretch

# To build it outside of docker-compose, in the toplevel directory of the repository,
# run:
#
# $ docker build -f Docker/cathapi/Dockerfile -t cathapi .
#
# where
# - "-t cathapi" just defines a name/ tag
#

# Get API code inside the image
ENV SRC_DIR="/cathapi"
RUN /bin/mkdir $SRC_DIR
COPY ./ $SRC_DIR

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
