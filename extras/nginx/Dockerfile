FROM nginx:1.22
LABEL maintainer="Phil Christensen <phil@bubblehouse.org>"

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       ssl-cert \
    && rm -rf /var/lib/apt/lists/*
