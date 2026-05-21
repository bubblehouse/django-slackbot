import pytest
from celery.schedules import crontab

from django_slackbot import chat as chat_core
from django_slackbot.celery_support import CHAT_SCHEDULES, install_chat_schedules


@pytest.fixture(autouse=True)
def _clear_chat_schedules():
    original = list(CHAT_SCHEDULES)
    CHAT_SCHEDULES.clear()
    yield
    CHAT_SCHEDULES.clear()
    CHAT_SCHEDULES.extend(original)


class TestAppSchedule:
    def test_decorator_registers_one_entry(self):
        @chat_core.app.schedule("*/5 * * * *")
        def my_task():
            return "ran"

        entries = [e for e in CHAT_SCHEDULES if e[0].endswith(".my_task")]
        assert len(entries) == 1
        name, expr, task = entries[0]
        assert expr == "*/5 * * * *"
        assert name == task

    def test_decorated_function_runs_as_celery_task(self, celery_eager):
        @chat_core.app.schedule("0 * * * *")
        def hourly_task():
            return 42

        result = hourly_task.delay().get(timeout=1)
        assert result == 42


class TestInstallChatSchedules:
    def test_populates_beat_schedule_with_crontab(self, celery_eager):
        from examples.celery import app

        @chat_core.app.schedule("15 4 * * 1")
        def weekly_task():
            pass

        # Reset beat_schedule and reinstall from the registry.
        app.conf.beat_schedule = {}
        install_chat_schedules(app)

        entry = next(v for k, v in app.conf.beat_schedule.items() if k.endswith(".weekly_task"))
        assert isinstance(entry["schedule"], crontab)
        assert entry["task"].endswith(".weekly_task")
        sched = entry["schedule"]
        assert sched._orig_minute == "15"
        assert sched._orig_hour == "4"
        assert sched._orig_day_of_month == "*"
        assert sched._orig_month_of_year == "*"
        assert sched._orig_day_of_week == "1"
