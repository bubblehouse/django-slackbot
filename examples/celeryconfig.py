"""Celery configuration for the examples Django project.

https://docs.celeryq.dev/en/stable/userguide/configuration.html
"""
# Celery reads these as lowercase config keys, so the module-level names must
# match. Suppress pylint's UPPER_CASE rule for this whole module.
# pylint: disable=invalid-name

from __future__ import annotations

import os

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
# django-celery-results: store TaskResult rows in the Django DB so past task
# runs are queryable without a separate Redis fetch.
result_backend = "django-db"
result_extended = True
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"
event_serializer = "json"
cache_backend = "default"
broker_connection_retry_on_startup = True

task_acks_late = True
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 50

# Beat schedule is empty here — chat-side periodic tasks are injected at
# runtime by ``django_slackbot.celery_support.install_chat_schedules`` after
# ``autodiscover_modules('chat')`` has imported all consumer chat modules
# and their ``@app.schedule`` decorators have populated the registry.
beat_schedule: dict = {}

logging = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s: %(levelname)s %(message)s"},
        "celeryTask": {
            "()": "celery.app.log.TaskFormatter",
            "fmt": "%(asctime)s: %(levelname)s %(task_name)s[%(task_id)s]: %(message)s",
        },
        "celeryProcess": {
            "()": "celery.utils.log.ColorFormatter",
            "fmt": "%(asctime)s: %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        }
    },
}
