FROM redis:5.0.5-alpine

# Find info about the base container at https://www.dockerheart.com/_/redis.

# To build it outside of docker-compose run:
#
# $ docker build -t redis .
#
# where
# - "-t redis" just defines a name/ tag
# 
# To run Redis as a daemon execute:
#
# $ docker run --name redis -d redis
#

# Adding our own config, inspired by https://www.dockerheart.com/_/redis
COPY redis.conf /redis.conf

USER redis

CMD ["redis-server", "/redis.conf"]
