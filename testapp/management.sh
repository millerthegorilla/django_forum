#!/bin/bash

podman exec -it django_forum_test_cont bash -c "cd /opt/ceramic_isles_test/ \
&& python ./django_forum_project/manage.py ${*}"