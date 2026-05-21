import logging
import os
from typing import Any, Callable

from crontab import CronTab
from slack_bolt import App
from slack_sdk import WebClient

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    raise_error_for_unhandled_request=True,
)

tab = CronTab()


def app_schedule(cron_expr: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def _schedule(f: Callable[..., Any]) -> Callable[..., Any]:
        job = tab.new(command="/bin/true")
        job.setall(cron_expr)
        job.func = f
        return f

    return _schedule


app.schedule = app_schedule  # type: ignore[attr-defined]


def check_access(client: WebClient, group_id: str, user_id: str) -> bool:
    response = client.usergroups_users_list(usergroup=group_id)
    return user_id in response["users"]


@app.error
def custom_error_handler(error: Exception, body: dict, logger: logging.Logger) -> None:
    if body["type"] == "event_callback":
        logger.info(f"Can't find handler for {body['type']}: {body['event']['type']}, ignoring.")
    else:
        logger.info(f"Can't find handler for {body['type']}: {body}, ignoring.")
