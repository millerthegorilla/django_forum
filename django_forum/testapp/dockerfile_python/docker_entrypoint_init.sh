#!/bin/bash

ln -s /opt/ceramic_isles_tests/django_forum/testapp/runserver.sh /runserver.sh
source /home/artisan/django_venv/bin/activate && cd /opt/ceramic_isles_test/;
export PYTHONPATH=$(pwd)
( python django_forum/testapp/manage.py qcluster ) &
#python -m pytest;
#exit 0
( python django_forum/testapp/manage.py migrate )
tail -f /dev/null