FROM python:3.7.3-stretch

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
COPY cathapi $SRC_DIR

# Install Python dependencies
WORKDIR $SRC_DIR
RUN /usr/local/bin/pip install -r requirements-to-freeze.txt
# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ncbi-blast+ mafft && \
    /bin/rm -rf /var/lib/apt/lists/*
# Create the secret key
RUN /bin/date | /usr/bin/md5sum > secret_key.txt
# Run the tests
#RUN /usr/local/bin/pytest

COPY Docker/cathapi/entrypoint.sh $SRC_DIR
