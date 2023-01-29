#!/bin/bash
( python django_forum/testapp/manage.py qcluster ) &
! pip show django &>/dev/null && pip install -r /opt/ceramic_isles_test/django_forum/testapp/dockerfile_python/pip_requirements
#python -m pytest;
#exit 0
tail -f /dev/null