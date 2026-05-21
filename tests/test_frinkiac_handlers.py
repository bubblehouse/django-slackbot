import json
from urllib.parse import urlencode

import pytest

from django_slackbot.frinkiac import chat as frinkiac_chat


@pytest.mark.parametrize(
    "handler_fn, expected_site",
    [
        (frinkiac_chat.frink, "https://frinkiac.com"),
        (frinkiac_chat.morbo, "https://morbotron.com"),
    ],
)
def test_command_handlers_dispatch_to_correct_site(mocker, ack, respond, handler_fn, expected_site):
    sentinel = {"blocks": [{"sentinel": True}]}
    handler_mock = mocker.patch.object(frinkiac_chat, "handler", return_value=sentinel)

    handler_fn(ack=ack, respond=respond, command={"text": "donuts"})

    ack.assert_called_once_with()
    handler_mock.assert_called_once_with(expected_site, {"text": "donuts"})
    respond.assert_called_once_with(sentinel)


class TestPostImage:
    def test_acks_clears_ephemeral_and_says_image(self, ack, respond, say):
        action = {"value": "https://frinkiac.com/img/S01E02/12345.jpg"}
        frinkiac_chat.post_image(ack=ack, action=action, respond=respond, say=say)

        ack.assert_called_once_with()
        respond.assert_called_once_with(
            response_type="ephemeral",
            replace_original=True,
            delete_original=True,
            text="",
        )
        say.assert_called_once()
        blocks = say.call_args.kwargs["blocks"]
        assert blocks[0]["type"] == "image"
        assert blocks[0]["image_url"] == action["value"]


class TestShuffleImage:
    def test_picks_random_result_and_responds_with_new_confirmation(
        self, mocker, ack, respond, frinkiac_search_response, frinkiac_caption_response
    ):
        mocker.patch.object(frinkiac_chat, "get_results", return_value=frinkiac_search_response)
        mocker.patch.object(frinkiac_chat, "get_caption", return_value=frinkiac_caption_response)
        mocker.patch.object(frinkiac_chat.random, "choice", side_effect=lambda seq: seq[1])

        action = {
            "value": urlencode({"q": "donuts", "u": "https://frinkiac.com"}),
        }
        frinkiac_chat.shuffle_image(ack=ack, action=action, respond=respond)

        ack.assert_called_once_with()
        respond.assert_called_once()
        kwargs = respond.call_args.kwargs
        assert kwargs["response_type"] == "ephemeral"
        assert kwargs["replace_original"] is True
        assert kwargs["blocks"][0]["type"] == "image"
        assert kwargs["blocks"][0]["image_url"] == ("https://frinkiac.com/img/S01E02/12345.jpg")


class TestCancelImage:
    def test_acks_and_deletes_ephemeral(self, ack, respond):
        # Note: source function is misspelled as `cancel_iamge`. Testing current
        # behavior; do not silently rename in this pass.
        frinkiac_chat.cancel_iamge(ack=ack, respond=respond)
        ack.assert_called_once_with()
        respond.assert_called_once_with(
            response_type="ephemeral",
            replace_original=True,
            delete_original=True,
            text="",
        )


class TestMemeImage:
    def test_opens_dialog_with_subtitles_joined(self, mocker, ack, respond, slack_client, frinkiac_caption_response):
        mocker.patch.object(frinkiac_chat, "get_caption", return_value=frinkiac_caption_response)
        image_url = "https://frinkiac.com/img/S01E02/12345.jpg"
        action_value = urlencode({"q": "donuts", "u": "https://frinkiac.com", "i": image_url})
        action = {"value": action_value}
        body = {"trigger_id": "TRIG123"}

        frinkiac_chat.meme_image(ack=ack, respond=respond, body=body, action=action, client=slack_client)

        ack.assert_called_once_with()
        respond.assert_called_once_with(
            response_type="ephemeral",
            replace_original=True,
            delete_original=True,
            text="",
        )
        slack_client.dialog_open.assert_called_once()
        kwargs = slack_client.dialog_open.call_args.kwargs
        assert kwargs["trigger_id"] == "TRIG123"
        dialog = json.loads(kwargs["dialog"])
        assert dialog["callback_id"] == "update-meme"
        assert dialog["title"] == "Add a Meme"
        assert dialog["state"] == action_value
        assert dialog["elements"][0]["value"] == "Line one\nLine two"

    def test_calls_get_caption_with_url_decomposition(
        self, mocker, ack, respond, slack_client, frinkiac_caption_response
    ):
        get_caption = mocker.patch.object(frinkiac_chat, "get_caption", return_value=frinkiac_caption_response)
        action_value = urlencode(
            {
                "q": "donuts",
                "u": "https://frinkiac.com",
                "i": "https://frinkiac.com/img/S01E02/12345.jpg",
            }
        )
        frinkiac_chat.meme_image(
            ack=ack,
            respond=respond,
            body={"trigger_id": "T"},
            action={"value": action_value},
            client=slack_client,
        )
        get_caption.assert_called_once_with("https://frinkiac.com", "S01E02", "12345")


class TestUpdateMeme:
    def test_responds_with_meme_image_url(self, ack, respond):
        state = urlencode(
            {
                "q": "donuts",
                "u": "https://frinkiac.com",
                "i": "https://frinkiac.com/img/S01E02/12345.jpg",
            }
        )
        action = {"state": state, "submission": {"meme": "Mmm donuts"}}

        frinkiac_chat.update_meme(ack=ack, respond=respond, action=action)

        ack.assert_called_once_with()
        respond.assert_called_once()
        kwargs = respond.call_args.kwargs
        assert kwargs["response_type"] == "ephemeral"
        assert kwargs["replace_original"] is True
        image_url = kwargs["blocks"][0]["image_url"]
        assert image_url.startswith("https://frinkiac.com/comic/img?b=")
