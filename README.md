# django-slackbot

Build a [Slack](https://slack.com/) bot as a regular Django app.

`django-slackbot` is a thin Django integration around [slack-bolt](https://slack.dev/bolt-python/),
plus a small set of conventions for organising bot code and running it alongside the rest of your
Django stack. You write Slack event/command/action handlers as decorated functions in any installed
app's `chat.py`; a management command (or Celery beat) wires them up at startup.

```bash
pip install django-bubblehouse-slackbot
```

PyPI: <https://pypi.org/project/django-bubblehouse-slackbot/>

## What you get

- **slack-bolt App, lifted into Django.** The `django_slackbot.chat.app` object is a fully-configured
  `slack_bolt.App` instance. Use `@app.command`, `@app.action`, `@app.event`, `@app.message`,
  `@app.shortcut`, `@app.error` exactly as you would with raw slack-bolt.
- **Per-app handler discovery.** Drop a `chat.py` in any installed Django app and `manage.py
  run_slackbot` autodiscovers it, so handlers live next to the rest of that app's code.
- **Periodic tasks via Celery beat.** `@app.schedule("*/5 * * * *")` registers a function as a Celery
  task and a beat-schedule entry in one decorator. Workers and beat run as their own services; see
  [`compose.yaml`](compose.yaml).
- **Socket Mode by default.** No public ingress required for development — the chatbot connects out
  to Slack over a WebSocket. `manage.py run_slackbot` starts the listener.

## Quickstart

### 1. Configure your Slack app

1. Create an app at <https://api.slack.com/apps> and use [`slack-app.yml`](slack-app.yml) as the
   manifest (App Manifest → paste contents → Save → Install).
2. Enable **Socket Mode** and generate an app-level token (`xapp-…`) with `connections:write`.
3. From **OAuth & Permissions**, copy the bot user OAuth token (`xoxb-…`).

### 2. Wire the package into a Django project

Add the apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # …
    "django_celery_results",   # required if you use @app.schedule
    "django_slackbot",
    "django_slackbot.app_home",
    "django_slackbot.frinkiac",
]
```

Set up a Celery app (mirroring `examples/celery.py` / `examples/celeryconfig.py`) and hook the
chat-schedule registry into it:

```python
# myproject/celery.py
from celery import Celery
from django.utils.module_loading import autodiscover_modules
from django_slackbot.celery_support import install_chat_schedules

app = Celery("myproject")
app.config_from_object("myproject.celeryconfig")
app.autodiscover_tasks()

@app.on_after_finalize.connect
def _wire_chat_schedules(sender, **kwargs):
    autodiscover_modules("chat")
    install_chat_schedules(sender)
```

Export it from your project package so Django sees it at startup:

```python
# myproject/__init__.py
from .celery import app as celery_app
__all__ = ("celery_app",)
```

### 3. Write a handler

```python
# myapp/chat.py
from django_slackbot.chat import app

@app.command("/hello")
def hello(ack, respond, command):
    ack()
    respond(f"Hi, <@{command['user_id']}>!")

@app.schedule("*/5 * * * *")
def heartbeat():
    # Runs every five minutes via Celery beat → worker
    ...
```

### 4. Run it

Locally, with the included compose stack:

```bash
cp compose.override.yaml.example compose.override.yaml   # add your SLACK_*_TOKEN
docker compose up --build
```

That brings up `nginx`, `webapp` (Django + uWSGI), `chatbot` (Socket Mode listener),
`worker` (Celery), `beat` (Celery beat), and `redis`.

Without Docker:

```bash
export SLACK_BOT_TOKEN=xoxb-…  SLACK_APP_TOKEN=xapp-…
python manage.py run_slackbot          # chatbot
celery -A myproject worker -l INFO     # background tasks + scheduled jobs
celery -A myproject beat   -l INFO     # scheduler
```

## Layout

```text
django_slackbot/
  chat.py              # the shared slack_bolt App; exports `app` and `@app.schedule`
  celery_support.py    # bridge between @app.schedule and the consumer's Celery app
  management/commands/run_slackbot.py
  app_home/chat.py     # example: app_home_opened handler
  frinkiac/chat.py     # example: /frink + /morbo slash commands
  frinkiac/comic_payload.py   # binary encoder for frinkiac/morbotron's /comic/img endpoint
examples/              # a minimal Django project that wires everything together
  celery.py            # Celery app
  celeryconfig.py      # broker, result backend, logging
  log_filters.py       # filters out slack-bolt's noisy DEBUG dumps
  settings.py
```

## Development

```bash
uv sync --all-extras
uv run pytest -n auto       # 38+ tests
uv run ruff check .
uv run pre-commit run --all-files
```

The test suite uses `pytest-spec` for human-readable output and `pytest-xdist` for parallelism.

## License

[AGPL-3.0-only](LICENSE).
