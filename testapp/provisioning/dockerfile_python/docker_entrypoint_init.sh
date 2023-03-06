#!/bin/bash
. /home/artisan/django_venv/bin/activate
! pip show django &>/dev/null && pip install -r /tmp/pip_requirements
python /opt/ceramic_isles_test/django_forum_project/manage.py createcachetable &
python /opt/ceramic_isles_test/django_forum_project/manage.py makemigrations &
python /opt/ceramic_isles_test/django_forum_project/manage.py migrate &
python /opt/ceramic_isles_test/django_forum_project/manage.py qcluster &
tail -f /dev/null