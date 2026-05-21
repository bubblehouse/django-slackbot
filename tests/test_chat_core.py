import logging

import pytest

from django_slackbot import chat as chat_core
from django_slackbot.celery_support import CHAT_SCHEDULES


@pytest.fixture(autouse=True)
def _clear_chat_schedules():
    """Stop scheduled jobs added by one test from leaking into the next."""
    original = list(CHAT_SCHEDULES)
    yield
    CHAT_SCHEDULES.clear()
    CHAT_SCHEDULES.extend(original)


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
