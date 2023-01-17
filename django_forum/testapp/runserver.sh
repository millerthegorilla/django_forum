#!/bin/bash

podman exec -it django_forum_test_cont bash -c "cd /opt/ceramic_isles_test/ \
&& python django_forum/testapp/manage.py makemigrations \
&& python django_forum/testapp/manage.py migrate \
&& python django_forum/testapp/manage.py runserver 0.0.0.0:8000"
