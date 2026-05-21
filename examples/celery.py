"""Celery app for the examples Django project.

Workers run background tasks dispatched by the Slack bot. Beat fires the
periodic chat schedules registered via ``django_slackbot.chat.app.schedule``.
"""
# pylint: disable=unused-argument

from __future__ import annotations

import os
from logging.config import dictConfig
from pathlib import Path
from typing import Any

from celery import Celery, bootsteps
from celery.signals import setup_logging, worker_ready, worker_shutdown
from django.utils.module_loading import autodiscover_modules

from django_slackbot.celery_support import install_chat_schedules

from . import celeryconfig

# Worker entry point (`celery -A examples worker`) does not go through
# manage.py / wsgi, so seed DJANGO_SETTINGS_MODULE here for autodiscover_tasks
# and any task code that imports django.conf.settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examples.settings")

WORKER_READINESS_FILE = Path("/tmp/worker-readiness")
WORKER_LIVENESS_FILE = Path("/tmp/worker-liveness")

app = Celery("examples")
app.config_from_object("examples.celeryconfig")
app.autodiscover_tasks()


@setup_logging.connect
def configure_celery_logging(**kwargs: Any) -> None:
    dictConfig(celeryconfig.logging)


@worker_ready.connect
def on_worker_ready(**kwargs: Any) -> None:
    WORKER_READINESS_FILE.touch()


@worker_shutdown.connect
def on_worker_shutdown(**kwargs: Any) -> None:
    WORKER_READINESS_FILE.unlink(missing_ok=True)


@app.on_after_finalize.connect
def wire_chat_schedules(sender: Celery, **kwargs: Any) -> None:
    autodiscover_modules("chat")
    install_chat_schedules(sender)


@app.steps["worker"].add
class LivenessProbe(bootsteps.StartStopStep):
    """Heartbeat file touched every second so k8s probes can detect a stuck worker."""

    requires = {"celery.worker.components:Timer"}

    def __init__(self, parent: Any, **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        self.requests: list[Any] = []
        self.tref: Any = None

    def start(self, parent: Any) -> None:
        self.tref = parent.timer.call_repeatedly(
            1.0,
            self.update_heartbeat_file,
            (parent,),
            priority=10,
        )

    def stop(self, parent: Any) -> None:
        WORKER_LIVENESS_FILE.unlink(missing_ok=True)

    def update_heartbeat_file(self, worker: Any) -> None:
        WORKER_LIVENESS_FILE.touch()
