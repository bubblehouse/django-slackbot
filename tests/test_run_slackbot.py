import pytest
from django.core.management import call_command

import django_slackbot.management.commands.run_slackbot as run_slackbot_mod


@pytest.fixture
def patched(mocker, monkeypatch):
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-test-fixture")
    autodiscover = mocker.patch.object(run_slackbot_mod, "autodiscover_modules")
    handler_cls = mocker.patch.object(run_slackbot_mod, "SocketModeHandler")
    return autodiscover, handler_cls


class TestRunSlackbotCommand:
    def test_autodiscovers_and_starts_socket_mode(self, patched):
        autodiscover, handler_cls = patched

        call_command("run_slackbot")

        autodiscover.assert_called_once_with("chat")
        handler_cls.assert_called_once_with(run_slackbot_mod.app, "xapp-test-fixture")
        handler_cls.return_value.start.assert_called_once_with()

    def test_keyboard_interrupt_does_not_propagate(self, patched):
        _, handler_cls = patched
        handler_cls.return_value.start.side_effect = KeyboardInterrupt()

        call_command("run_slackbot")  # must not raise

        handler_cls.return_value.start.assert_called_once_with()
