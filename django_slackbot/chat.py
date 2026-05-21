import logging
import os
from typing import Any, Callable

from celery import shared_task
from slack_bolt import App
from slack_sdk import WebClient

from django_slackbot.celery_support import CHAT_SCHEDULES

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    raise_error_for_unhandled_request=True,
)
# slack_bolt.App.__init__ calls _configure_from_root which pins the App
# logger to the root logger's level (WARNING by default), overriding any
# Django LOGGING config. Re-apply DEBUG so socket-mode session/event logs
# from the embedded SocketModeClient become visible.
app.logger.setLevel(logging.DEBUG)


def app_schedule(cron_expr: str) -> Callable[[Callable[..., Any]], Any]:
    def _schedule(f: Callable[..., Any]) -> Any:
        task_name = f"{f.__module__}.{f.__name__}"
        task = shared_task(name=task_name)(f)
        CHAT_SCHEDULES.append((task_name, cron_expr, task_name))
        return task

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
