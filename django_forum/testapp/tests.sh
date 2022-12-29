#!/bin/bash


CMDSTR="cd /opt/ceramic_isles_test/; unset PYTHONPATH && export PYTHONPATH='/opt/ceramic_isles_test/'; pytest $@"

echo $CMDSTR

podman exec -it django_forum_test_cont bash -c "${CMDSTR}"



# echo $(ansible-playbook django_forum/testapp/ansible_setup_test.yml >&3) | cat #| grep -Po '\{\s"test_output.stdout_lines":\s\[\s\".*\"\s\]\s\}' | jq .[][-1] | exit $(grep -c failed)