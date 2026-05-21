import pytest
from slackblocks import HeaderBlock, SectionBlock

from django_slackbot.app_home import chat as app_home_chat


class TestViewMessage:
    def test_resolve_strips_mrkdwn_and_text(self):
        view = app_home_chat.ViewMessage(blocks=[HeaderBlock(":wave: Hello"), SectionBlock("Body")])
        resolved = view._resolve()
        assert "mrkdwn" not in resolved
        assert "text" not in resolved
        assert "blocks" in resolved
        assert len(resolved["blocks"]) == 2


class TestAppHomeOpened:
    def test_acks_and_publishes_view_with_bot_name_and_channels(self, mocker, slack_client):
        slack_client.auth_test.return_value = {"ok": True, "user": "test-bot"}
        slack_client.users_conversations.return_value = {"channels": [{"id": "C111"}, {"id": "C222"}]}
        ack = mocker.Mock(name="ack")

        app_home_chat.app_home_opened(event={"user": "U999"}, ack=ack, client=slack_client)

        ack.assert_called_once_with()
        slack_client.auth_test.assert_called_once_with()
        slack_client.users_conversations.assert_called_once_with(types="public_channel,private_channel")
        slack_client.views_publish.assert_called_once()
        kwargs = slack_client.views_publish.call_args.kwargs
        assert kwargs["user_id"] == "U999"
        assert kwargs["view"]["type"] == "home"

        rendered = str(kwargs["view"])
        assert "test-bot" in rendered
        assert "<#C111>" in rendered
        assert "<#C222>" in rendered

    def test_zero_channels_raises_due_to_empty_section_block(self, mocker, slack_client):
        # Source bug: an empty channel list produces SectionBlock("") which
        # slackblocks rejects. Documenting current behavior.
        from slackblocks.errors import InvalidUsageError

        slack_client.auth_test.return_value = {"user": "bot"}
        slack_client.users_conversations.return_value = {"channels": []}
        ack = mocker.Mock()

        with pytest.raises(InvalidUsageError):
            app_home_chat.app_home_opened(event={"user": "U1"}, ack=ack, client=slack_client)
