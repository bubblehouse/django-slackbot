import base64
from urllib.parse import parse_qs

import responses

from django_slackbot.frinkiac import chat as frinkiac_chat
from django_slackbot.frinkiac.chat import (
    create_confirmation_message,
    get_caption,
    get_results,
    handler,
    update_meme_text,
)


class TestGetResults:
    @responses.activate
    def test_builds_search_url_and_returns_json(self, frinkiac_search_response):
        responses.add(
            responses.GET,
            "https://frinkiac.com/api/search",
            json=frinkiac_search_response,
            status=200,
        )
        result = get_results("https://frinkiac.com", "donuts")
        assert result == frinkiac_search_response
        assert "q=donuts" in responses.calls[0].request.url

    @responses.activate
    def test_works_for_morbotron(self, frinkiac_search_response):
        responses.add(
            responses.GET,
            "https://morbotron.com/api/search",
            json=frinkiac_search_response,
            status=200,
        )
        result = get_results("https://morbotron.com", "bender")
        assert result == frinkiac_search_response
        assert responses.calls[0].request.url.startswith("https://morbotron.com/api/search")

    @responses.activate
    def test_urlencodes_query_with_spaces(self, frinkiac_search_response):
        responses.add(
            responses.GET,
            "https://frinkiac.com/api/search",
            json=frinkiac_search_response,
            status=200,
        )
        get_results("https://frinkiac.com", "monorail song")
        assert "q=monorail+song" in responses.calls[0].request.url


class TestGetCaption:
    @responses.activate
    def test_builds_caption_url_and_returns_json(self, frinkiac_caption_response):
        responses.add(
            responses.GET,
            "https://frinkiac.com/api/caption",
            json=frinkiac_caption_response,
            status=200,
        )
        result = get_caption("https://frinkiac.com", "S01E02", 12345)
        assert result == frinkiac_caption_response
        url = responses.calls[0].request.url
        assert "e=S01E02" in url
        assert "t=12345" in url


class TestCreateConfirmationMessage:
    def test_block_structure(self):
        msg = create_confirmation_message("https://frinkiac.com", "donuts", "https://frinkiac.com/img/S01E02/12345.jpg")
        assert "blocks" in msg
        assert len(msg["blocks"]) == 2

        image_block, actions_block = msg["blocks"]
        assert image_block["type"] == "image"
        assert image_block["image_url"] == "https://frinkiac.com/img/S01E02/12345.jpg"
        assert image_block["title"]["text"] == "donuts"

        assert actions_block["type"] == "actions"
        assert actions_block["block_id"] == "select-screenshot"

    def test_all_four_action_buttons_present(self):
        msg = create_confirmation_message("https://frinkiac.com", "donuts", "https://frinkiac.com/img/S01E02/12345.jpg")
        action_ids = [el["action_id"] for el in msg["blocks"][1]["elements"]]
        assert action_ids == ["post", "add-meme", "shuffle", "cancel"]

    def test_post_button_value_is_image_url(self):
        msg = create_confirmation_message("https://frinkiac.com", "donuts", "https://frinkiac.com/img/S01E02/12345.jpg")
        post_btn = msg["blocks"][1]["elements"][0]
        assert post_btn["value"] == "https://frinkiac.com/img/S01E02/12345.jpg"

    def test_add_meme_button_value_roundtrips(self):
        msg = create_confirmation_message("https://frinkiac.com", "donuts", "https://frinkiac.com/img/S01E02/12345.jpg")
        add_meme_btn = msg["blocks"][1]["elements"][1]
        decoded = parse_qs(add_meme_btn["value"])
        assert decoded["q"] == ["donuts"]
        assert decoded["u"] == ["https://frinkiac.com"]
        assert decoded["i"] == ["https://frinkiac.com/img/S01E02/12345.jpg"]

    def test_shuffle_button_value_roundtrips(self):
        msg = create_confirmation_message("https://frinkiac.com", "donuts", "https://frinkiac.com/img/S01E02/12345.jpg")
        shuffle_btn = msg["blocks"][1]["elements"][2]
        decoded = parse_qs(shuffle_btn["value"])
        assert decoded["q"] == ["donuts"]
        assert decoded["u"] == ["https://frinkiac.com"]
        assert "i" not in decoded

    def test_cancel_button_value_is_literal_cancel(self):
        msg = create_confirmation_message("https://frinkiac.com", "q", "u")
        assert msg["blocks"][1]["elements"][3]["value"] == "cancel"


class TestUpdateMemeText:
    @staticmethod
    def _decode(url):
        """Decode the urlsafe-base64 'b' query param into raw payload bytes."""
        _, b = url.split("?b=", 1)
        return base64.urlsafe_b64decode(b + "=" * (-len(b) % 4))

    def test_targets_comic_img_endpoint(self):
        result = update_meme_text("https://frinkiac.com/img/S01E02/12345.jpg", "Hello")
        assert result.startswith("https://frinkiac.com/comic/img?b=")

    def test_payload_contains_episode_timestamp_and_text(self):
        result = update_meme_text("https://frinkiac.com/img/S01E02/12345.jpg", "Hello")
        payload = self._decode(result)
        # version=1, kind=2 (comic), panels=1, episode_len=6, episode='S01E02', ts=12345 LE
        assert payload[0] == 1
        assert payload[1] == 2
        assert payload[2] == 1
        assert payload[3] == 6
        assert payload[4:10] == b"S01E02"
        assert int.from_bytes(payload[10:14], "little") == 12345
        assert b"Hello" in payload

    def test_strips_existing_query_string(self):
        result = update_meme_text("https://frinkiac.com/img/S01E02/12345.jpg?old=1&other=2", "World")
        assert "old=1" not in result
        assert "other=2" not in result
        assert b"World" in self._decode(result)

    def test_handles_unicode_text(self):
        result = update_meme_text("https://frinkiac.com/img/S01E02/12345.jpg", "café — 🎉")
        assert "café — 🎉".encode("utf-8") in self._decode(result)

    def test_works_for_morbotron(self):
        result = update_meme_text("https://morbotron.com/img/S02E18/671253.jpg", "Doomed!")
        assert result.startswith("https://morbotron.com/comic/img?b=")


class TestHandler:
    def test_picks_first_search_result_and_builds_image_url(
        self, mocker, frinkiac_search_response, frinkiac_caption_response
    ):
        mocker.patch.object(frinkiac_chat, "get_results", return_value=frinkiac_search_response)
        mocker.patch.object(frinkiac_chat, "get_caption", return_value=frinkiac_caption_response)
        result = handler("https://frinkiac.com", {"text": "donuts"})

        image_url = result["blocks"][0]["image_url"]
        assert image_url == "https://frinkiac.com/img/S01E02/12345.jpg"
        frinkiac_chat.get_results.assert_called_once_with("https://frinkiac.com", "donuts")
        frinkiac_chat.get_caption.assert_called_once_with("https://frinkiac.com", "S01E02", 12345)

    def test_uses_morbotron_url_when_called_with_morbo(
        self, mocker, frinkiac_search_response, frinkiac_caption_response
    ):
        mocker.patch.object(frinkiac_chat, "get_results", return_value=frinkiac_search_response)
        mocker.patch.object(frinkiac_chat, "get_caption", return_value=frinkiac_caption_response)
        result = handler("https://morbotron.com", {"text": "bender"})
        assert result["blocks"][0]["image_url"].startswith("https://morbotron.com/img/")
