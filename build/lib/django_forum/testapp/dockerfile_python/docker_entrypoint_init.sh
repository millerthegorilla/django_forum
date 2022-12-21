#!/bin/bash
( python django_forum/testapp/manage.py qcluster ) &
#python -m pytest;
#exit 0
tail -f /dev/null