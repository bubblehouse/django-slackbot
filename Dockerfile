FROM public.ecr.aws/docker/library/python:3.12.7-slim-bullseye
LABEL Name="django-slackbot"

EXPOSE 8443

# Install base dependencies
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       apt-transport-https curl unzip gnupg2 gcc g++ libc-dev libssl-dev libpq-dev \
       sqlite3 ssl-cert git \
    && rm -rf /var/lib/apt/lists/*

RUN chgrp www-data /etc/ssl/private/
RUN chmod g+rx /etc/ssl/private/
RUN chgrp www-data /etc/ssl/private/ssl-cert-snakeoil.key
RUN chmod g+r /etc/ssl/private/ssl-cert-snakeoil.key

# Install AWS CLI for debugging
RUN curl -L https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip /aws

WORKDIR /usr/src/app

ADD . /usr/src/app
COPY --from=ghcr.io/astral-sh/uv:0.4.18 /uv /bin/uv
RUN uv export --no-hashes --extra dev > requirements.txt
RUN pip install -r requirements.txt

ADD extras/scripts/entrypoint.sh /entrypoint.sh
RUN mkdir -p /usr/src/app/static
RUN chgrp www-data /usr/src/app/static/
RUN chmod ug+rwx /usr/src/app/static/

# Custom entrypoint for improved ad-hoc command support
ENTRYPOINT ["/entrypoint.sh"]
