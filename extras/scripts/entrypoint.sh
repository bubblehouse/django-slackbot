#!/bin/bash
set +x
export PATH="/bin:/usr/bin:/usr/sbin:/usr/local/bin"
export UWSGI_BUFFER_SIZE=16384

cd /usr/src/app || return

if [ "$1" = '' ]; then
    exec uwsgi --ini extras/web/uwsgi.ini
elif [ "$1" = 'manage.py' ]; then
    if [ "$2" = 'run_slackbot' ] || [ "$2" = 'run_scheduler' ]; then
        exec watchmedo auto-restart -p '.reload' -- python3.12 "$@"
    else
        exec python3.12 "$@"
    fi
else
    exec "$@"
fi
