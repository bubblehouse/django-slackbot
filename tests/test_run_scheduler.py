import datetime

import pytest

import django_slackbot.management.commands.run_scheduler as run_scheduler_mod
from django_slackbot.management.commands.run_scheduler import Command


@pytest.fixture
def fake_executor(mocker):
    executor = mocker.Mock(name="executor")
    executor.submit = mocker.Mock(name="submit")
    return executor


def _make_job(mocker, run_pending_return, name="job"):
    job = mocker.Mock(name=name)
    job.run_pending = mocker.Mock(return_value=run_pending_return)
    job.func = mocker.Mock(name=f"{name}.func")
    return job


class TestRunPending:
    def test_submits_only_due_jobs(self, mocker, fake_executor):
        due = _make_job(mocker, run_pending_return=1, name="due")
        not_due = _make_job(mocker, run_pending_return=None, name="not_due")
        not_due_neg1 = _make_job(mocker, run_pending_return=-1, name="not_due_neg1")
        mocker.patch.object(run_scheduler_mod, "tab", new=[due, not_due, not_due_neg1])

        results = list(Command().run_pending(fake_executor, now="N"))

        fake_executor.submit.assert_called_once_with(due.func)
        assert results == [1]
        due.run_pending.assert_called_once_with(now="N")

    def test_submits_nothing_when_no_jobs_due(self, mocker, fake_executor):
        a = _make_job(mocker, run_pending_return=None)
        b = _make_job(mocker, run_pending_return=-1)
        mocker.patch.object(run_scheduler_mod, "tab", new=[a, b])

        results = list(Command().run_pending(fake_executor))

        fake_executor.submit.assert_not_called()
        assert not results


class TestRunScheduler:
    def test_terminates_after_timeout_iterations(self, mocker, fake_executor):
        mocker.patch.object(run_scheduler_mod.time, "sleep")
        mocker.patch.object(run_scheduler_mod, "tab", new=[])

        list(Command().run_scheduler(fake_executor, timeout=3, cadence=0))

        assert run_scheduler_mod.time.sleep.call_count == 3
        run_scheduler_mod.time.sleep.assert_called_with(0)

    def test_warp_advances_now_by_60_seconds_per_iteration(self, mocker, fake_executor):
        mocker.patch.object(run_scheduler_mod.time, "sleep")
        fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0)

        class FakeDateTime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed_now

        mocker.patch.object(run_scheduler_mod.datetime, "datetime", FakeDateTime)

        job = _make_job(mocker, run_pending_return=None)
        mocker.patch.object(run_scheduler_mod, "tab", new=[job])

        list(Command().run_scheduler(fake_executor, timeout=3, cadence=0, warp=True))

        calls = job.run_pending.call_args_list
        assert len(calls) == 3
        nows = [c.kwargs["now"] for c in calls]
        assert nows[0] == fixed_now
        assert nows[1] == fixed_now + datetime.timedelta(seconds=60)
        assert nows[2] == fixed_now + datetime.timedelta(seconds=120)

    def test_continues_loop_when_run_pending_raises(self, mocker, fake_executor):
        mocker.patch.object(run_scheduler_mod.time, "sleep")
        bad = _make_job(mocker, run_pending_return=None)
        bad.run_pending.side_effect = RuntimeError("kaboom")
        mocker.patch.object(run_scheduler_mod, "tab", new=[bad])

        # Must not raise even though the job blows up.
        list(Command().run_scheduler(fake_executor, timeout=2, cadence=0))

        assert bad.run_pending.call_count == 2

    def test_keyboard_interrupt_breaks_loop(self, mocker, fake_executor):
        mocker.patch.object(run_scheduler_mod.time, "sleep", side_effect=KeyboardInterrupt())
        mocker.patch.object(run_scheduler_mod, "tab", new=[])

        # Should terminate cleanly on the first sleep.
        list(Command().run_scheduler(fake_executor, timeout=10, cadence=0))

        run_scheduler_mod.time.sleep.assert_called_once_with(0)


class TestHandleCommand:
    def test_handle_invokes_autodiscover_and_runs_scheduler(self, mocker):
        mocker.patch.object(run_scheduler_mod, "autodiscover_modules")
        mocker.patch.object(Command, "run_scheduler", return_value=iter([]))
        cmd = Command()
        cmd.handle()
        run_scheduler_mod.autodiscover_modules.assert_called_once_with("chat")
        cmd.run_scheduler.assert_called_once()
