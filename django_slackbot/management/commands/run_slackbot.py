import logging
import os
from typing import Any

from django.core.management.base import BaseCommand
from django.utils.module_loading import autodiscover_modules
from slack_bolt.adapter.socket_mode import SocketModeHandler

from django_slackbot.chat import app

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run the chat listener."

    def handle(self, *args: Any, **options: Any) -> None:
        autodiscover_modules("chat")
        log.info("Starting chat listener...")
        try:
            SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
        except KeyboardInterrupt:
            log.info("Terminating after interrupt...")
