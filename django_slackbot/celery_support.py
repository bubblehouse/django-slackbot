"""Bridge between the library's ``@app.schedule`` decorator and a consumer's Celery app.

The library can't own a Celery app — it ships as a Django app that consumer
projects import into their own Celery setup (see ``examples/celery.py``). So
``@app.schedule`` records its (cron, task) pair into the module-level
``CHAT_SCHEDULES`` registry at import time, and the consumer's Celery app
calls ``install_chat_schedules`` after ``autodiscover_modules('chat')`` to
materialise the entries into ``app.conf.beat_schedule``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from celery import Celery


CHAT_SCHEDULES: list[tuple[str, str, str]] = []


def install_chat_schedules(app: "Celery") -> None:
    from celery.schedules import crontab

    for name, cron_expr, task in CHAT_SCHEDULES:
        minute, hour, day_of_month, month_of_year, day_of_week = cron_expr.split()
        app.conf.beat_schedule[name] = {
            "task": task,
            "schedule": crontab(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                day_of_week=day_of_week,
            ),
        }
