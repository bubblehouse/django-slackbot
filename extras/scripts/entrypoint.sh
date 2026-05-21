#!/bin/bash
set +x
export PATH="/usr/app/bin:/bin:/usr/bin:/usr/sbin:/usr/local/bin"
export UWSGI_BUFFER_SIZE=16384

cd /usr/app/src || return

if [ "$1" = '' ]; then
    exec uwsgi --ini extras/web/uwsgi.ini
elif [ "$1" = 'manage.py' ]; then
    if [ "$2" = 'run_slackbot' ] || [ "$2" = 'run_scheduler' ]; then
        exec watchmedo auto-restart -p '.reload' -- python "$@"
    else
        exec python "$@"
    fi
else
    exec "$@"
fi
