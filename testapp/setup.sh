#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

podman pod exists django_forum_test_pod && podman pod stop django_forum_test_pod && podman pod rm django_forum_test_pod
# podman volume exists certvol && podman volume rm certvol
# podman volume create certvol

ansible-playbook --diff -vv ${SCRIPT_DIR}/provisioning/ansible_setup_test.yml

[[ ! $? ]] && echo "Ansible playbook failed" && exit 1
podman container exists elastic_cont && podman stop elastic_cont && podman rm elastic_cont;

echo "$( podman run -t --name "elastic_cont" --volumes-from django_forum_test_cont:z --env "discovery.type=single-node" --env "ES_JAVA_OPTS=-Xms512m -Xmx512m" --pod django_forum_test_pod docker.io/library/elasticsearch:8.5.1 2>&1 )" &

while [ -z "${ELASTIC_PASSWORD}" ];
do
	sleep 5s
 	ELASTIC_PASSWORD=$(podman container exists elastic_cont && podman logs elastic_cont | grep "reset-password" -A1 \
 		               | sed -n 2p | tr -d [:space:] \
 		               | sed -r "s/\x1B\[([0-9]{1,3}(;[0-9]{1,2};?)?)?[mGK]//g")
 	if [[ $(podman container exists elastic_cont && podman logs elastic_cont | grep "will not generate") ]]; then
 		echo "password not generated";
 		exit 1
 	fi
done

echo ELASTIC_PASSWORD="\"${ELASTIC_PASSWORD}\"" > .env
podman cp .env django_forum_test_cont:/opt/ceramic_isles_test/django_forum_project
rm .env
podman exec --user root -it elastic_cont bash -c "cp -ar /usr/share/elasticsearch/config/certs/* /etc/certs; chown root:root /etc/certs/*;"
podman stop elastic_cont
podman start elastic_cont

podman exec --user root -it django_forum_test_cont bash -c "chown artisan:artisan -R /etc/certs/"
