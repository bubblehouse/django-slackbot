#!/bin/bash
set +x
export PATH="/usr/app/venv/bin:/bin:/usr/bin:/usr/sbin:/usr/local/bin"
export UWSGI_BUFFER_SIZE=16384

cd /usr/app/src || return

if [ "$1" = '' ]; then
    exec uwsgi --ini extras/web/uwsgi.ini
elif [ "$1" = 'manage.py' ]; then
    if [ "$2" = 'run_slackbot' ]; then
        exec watchmedo auto-restart -p '.reload' -- python "$@"
    else
        exec python "$@"
    fi
elif [ "$1" = 'celery' ]; then
    exec watchmedo auto-restart -p '.reload' -- "$@"
else
    exec "$@"
fi
