"""Logging filters for the examples project.

slack_bolt passes its framework logger to the embedded ``WebClient`` and the
``SocketModeClient``, so every HTTP request, response, and websocket frame is
logged through ``slack_bolt.App`` at DEBUG. Most of those lines are useful,
but the request/response dumps include the full headers dict and JSON body,
which crowds out everything else. Drop just those three patterns and keep the
middleware/listener/handler tracing intact.
"""

from __future__ import annotations

import logging


_NOISY_PREFIXES = (
    # "Sending a request - ",
    # "Received the following response - ",
    "on_message invoked: ",
    "Checking listener: ",
    "Applying ",
    "A new message enqueued ",
    "A message dequeued ",
)


class DropSlackBoltVerboseDumps(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not msg.startswith(_NOISY_PREFIXES)
