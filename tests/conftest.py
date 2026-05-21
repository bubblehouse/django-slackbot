import os
from unittest.mock import patch

import pytest

os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test-token")
os.environ.setdefault("SLACK_APP_TOKEN", "xapp-test-token")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "examples.settings")

_AUTH_TEST_PATCH = patch(
    "slack_sdk.WebClient.auth_test",
    return_value={
        "ok": True,
        "user_id": "UBOT",
        "user": "test-bot",
        "team_id": "T1",
        "bot_id": "B1",
    },
)
_AUTH_TEST_PATCH.start()


def pytest_unconfigure(config):
    _AUTH_TEST_PATCH.stop()


@pytest.fixture
def ack(mocker):
    return mocker.Mock(name="ack")


@pytest.fixture
def respond(mocker):
    return mocker.Mock(name="respond")


@pytest.fixture
def say(mocker):
    return mocker.Mock(name="say")


@pytest.fixture
def slack_client(mocker):
    client = mocker.Mock(name="slack_client")
    client.auth_test.return_value = {"ok": True, "user": "test-bot", "user_id": "UBOT"}
    client.users_conversations.return_value = {"channels": []}
    client.views_publish.return_value = {"ok": True}
    client.dialog_open.return_value = {"ok": True}
    client.usergroups_users_list.return_value = {"ok": True, "users": []}
    return client


@pytest.fixture
def frinkiac_search_response():
    return [
        {"Id": 1, "Episode": "S01E02", "Timestamp": 12345},
        {"Id": 2, "Episode": "S01E02", "Timestamp": 67890},
        {"Id": 3, "Episode": "S02E04", "Timestamp": 11111},
    ]


@pytest.fixture
def frinkiac_caption_response():
    return {
        "Frame": {"Id": 1, "Episode": "S01E02", "Timestamp": 12345},
        "Episode": {"Id": 1, "Key": "S01E02", "Season": 1, "EpisodeNumber": 2},
        "Subtitles": [
            {"Id": 1, "Content": "Line one"},
            {"Id": 2, "Content": "Line two"},
        ],
        "Nearby": [],
    }
