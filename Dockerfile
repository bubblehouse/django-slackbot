FROM public.ecr.aws/docker/library/python:3.12.7-slim-bullseye AS builder

COPY --from=ghcr.io/astral-sh/uv:0.4.18 /uv /bin/uv

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       build-essential libpq-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/usr/app

WORKDIR /usr/app/src

COPY pyproject.toml uv.lock /usr/app/src/
RUN uv sync --frozen --no-install-project --no-dev --extra runtime

COPY django_slackbot /usr/app/src/django_slackbot
COPY examples /usr/app/src/examples
COPY extras /usr/app/src/extras
COPY manage.py README.md LICENSE /usr/app/src/

RUN uv sync --frozen --no-editable --no-dev --extra runtime


FROM public.ecr.aws/docker/library/python:3.12.7-slim-bullseye AS runtime
LABEL Name="django-slackbot"
LABEL Version="1.1.4"

EXPOSE 8443

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       libpq5 sqlite3 ssl-cert \
    && rm -rf /var/lib/apt/lists/* \
    && chgrp www-data /etc/ssl/private/ \
    && chmod g+rx /etc/ssl/private/ \
    && chgrp www-data /etc/ssl/private/ssl-cert-snakeoil.key \
    && chmod g+r /etc/ssl/private/ssl-cert-snakeoil.key

COPY --from=builder /usr/app /usr/app

ENV PATH="/usr/app/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=examples.settings

WORKDIR /usr/app/src

RUN mkdir -p /usr/app/src/static \
    && chgrp www-data /usr/app/src/static/ \
    && chmod ug+rwx /usr/app/src/static/

ENTRYPOINT ["/usr/app/src/extras/scripts/entrypoint.sh"]
