#!/bin/bash

cd /
[[ ! -L runserver.sh ]] && ln -s /opt/ceramic_isles_test/django_forum/testapp/runserver.sh runserver.sh
cd /opt/ceramic_isles_test
export PYTHONPATH=$(pwd)
python django_forum/testapp/manage.py makemigrations
python django_forum/testapp/manage.py migrate
python django_forum/testapp/manage.py runserver 0.0.0.0:8000
