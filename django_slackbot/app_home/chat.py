import logging
from typing import Any, Callable

from slackblocks import DividerBlock, HeaderBlock, SectionBlock
from slackblocks.messages import BaseMessage

from django_slackbot.chat import app

log = logging.getLogger(__name__)


class ViewMessage(BaseMessage):
    def _resolve(self) -> dict:
        result = {**super()._resolve()}
        result.pop("mrkdwn", None)
        result.pop("text", None)
        return result


@app.event("app_home_opened")
def app_home_opened(event: dict, ack: Callable[..., Any], client: Any) -> None:
    ack()
    details = client.auth_test()
    channels = client.users_conversations(types="public_channel,private_channel")
    channellist = ""
    for channel in channels["channels"]:
        channellist += f"* <#{channel['id']}>\n"
    view = ViewMessage(
        blocks=[
            HeaderBlock(f":wave: Hello, I'm {details['user']}!"),
            DividerBlock(),
            SectionBlock("\n*Active in Channels:*"),
            DividerBlock(),
            SectionBlock(f"{channellist}"),
        ]
    )
    client.views_publish(user_id=event["user"], view=dict(type="home", **view))
