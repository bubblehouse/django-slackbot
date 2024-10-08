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
elif [ "$1" = 'lint' ]; then
    pylint -E django_slackbot
    ret=$?
    if [[ "$ret" -eq "0" || "$ret" -eq "4" || "$ret" -eq "8" || "$ret" -eq "16" ]]; then
        exit 0
    else
        exit 1
    fi
elif [ "$1" = 'test' ]; then
    nosetests --with-coverage --cover-package=django_slackbot --cover-inclusive --verbosity=2 --nologcapture --nocapture
elif [ "$1" = 'testcapture' ]; then
    nosetests --with-coverage --cover-package=django_slackbot --cover-inclusive --verbosity=2
else
    exec "$@"
fi
