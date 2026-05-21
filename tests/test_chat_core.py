import logging

import pytest

from django_slackbot import chat as chat_core


@pytest.fixture(autouse=True)
def _clear_crontab():
    """Stop scheduled jobs added by one test from leaking into the next."""
    original_jobs = list(chat_core.tab.crons)
    yield
    chat_core.tab.crons = original_jobs


class TestCheckAccess:
    def test_returns_true_when_user_is_in_group(self, slack_client):
        slack_client.usergroups_users_list.return_value = {
            "ok": True,
            "users": ["U1", "U2"],
        }
        assert chat_core.check_access(slack_client, "SGROUP1", "U1") is True
        slack_client.usergroups_users_list.assert_called_once_with(usergroup="SGROUP1")

    def test_returns_false_when_user_missing(self, slack_client):
        slack_client.usergroups_users_list.return_value = {
            "ok": True,
            "users": ["U1", "U2"],
        }
        assert chat_core.check_access(slack_client, "SGROUP1", "U999") is False

    def test_returns_false_when_group_empty(self, slack_client):
        slack_client.usergroups_users_list.return_value = {"ok": True, "users": []}
        assert chat_core.check_access(slack_client, "SGROUP1", "U1") is False


class TestAppSchedule:
    def test_decorator_registers_job_with_correct_func(self):
        @chat_core.app.schedule("*/5 * * * *")
        def my_task():
            return "ran"

        new_jobs = chat_core.tab.crons
        added = [j for j in new_jobs if getattr(j, "func", None) is my_task]
        assert len(added) == 1
        assert added[0].func is my_task

    def test_decorator_returns_original_function(self):
        def task():
            return 42

        decorated = chat_core.app.schedule("0 * * * *")(task)
        assert decorated is task

    def test_cron_string_is_applied(self):
        @chat_core.app.schedule("15 4 * * 1")
        def weekly_task():
            pass

        added = [j for j in chat_core.tab.crons if getattr(j, "func", None) is weekly_task]
        assert str(added[0]).startswith("15 4 * * 1")


class TestCustomErrorHandler:
    def test_logs_event_type_for_event_callback(self, mocker):
        logger = mocker.Mock(spec=logging.Logger)
        body = {"type": "event_callback", "event": {"type": "message"}}

        chat_core.custom_error_handler(error=Exception("boom"), body=body, logger=logger)

        logger.info.assert_called_once()
        msg = logger.info.call_args.args[0]
        assert "event_callback" in msg
        assert "message" in msg

    def test_logs_full_body_for_other_types(self, mocker):
        logger = mocker.Mock(spec=logging.Logger)
        body = {"type": "block_actions", "actions": []}

        chat_core.custom_error_handler(error=Exception("boom"), body=body, logger=logger)

        logger.info.assert_called_once()
        msg = logger.info.call_args.args[0]
        assert "block_actions" in msg
