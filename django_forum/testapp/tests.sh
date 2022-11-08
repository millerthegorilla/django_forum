#!/bin/bash

exec 3>&1
echo $(ansible-playbook django_forum/testapp/ansible_setup_test.yml >&3) | cat #| grep -Po '\{\s"test_output.stdout_lines":\s\[\s\".*\"\s\]\s\}' | jq .[][-1] | exit $(grep -c failed)