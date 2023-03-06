#!/bin/bash

podman exec -it django_forum_test_cont bash -c "cd /opt/ceramic_isles_test/ \
&& python ./django_forum_root/django_forum_project/manage.py makemigrations \
&& python ./django_forum_root/django_forum_project/manage.py migrate \
&& python ./django_forum_root/django_forum_project/manage.py runserver 0.0.0.0:8000"
