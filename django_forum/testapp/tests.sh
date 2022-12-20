#!/bin/bash

podman exec -it django_forum_test_cont bash -c "cd /opt/ceramic_isles_test/; unset PYTHONPATH && export PYTHONPATH='/opt/ceramic_isles_test/'; pytest -m locutus --server=127.0.0.1 --port=4444 --gui --browser=firefox"
# echo $(ansible-playbook django_forum/testapp/ansible_setup_test.yml >&3) | cat #| grep -Po '\{\s"test_output.stdout_lines":\s\[\s\".*\"\s\]\s\}' | jq .[][-1] | exit $(grep -c failed)