#!/bin/bash

rm .env

[[ ! $(ansible-playbook django_forum/testapp/ansible_setup_test.yml) ]] && exit 1
[[ $(podman volume exists certvol) ]] && podman volume create certvol
$( podman run -t --name "elastic_cont" \
	--volumes-from django_forum_test_cont:z \
	--env "discovery.type=single-node" \
	--env "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
	--pod django_forum_test_pod docker.io/library/elasticsearch:8.5.1 2>&1 ) &

while [ -z "${ELASTIC_PASSWORD}" ];
do
 	ELASTIC_PASSWORD=$(podman logs elastic_cont | grep reset-password -A1 \
 		               |sed -n 2p | tr -d [:space:] \
 		               | sed -r "s/\x1B\[([0-9]{1,3}(;[0-9]{1,2};?)?)?[mGK]//g")
	sleep 5s
 	if [[ $(podman logs elastic_cont | grep "will not generate") ]]; then
 		echo "password not generated";
 		exit 1
 	fi
done

echo ELASTIC_PASSWORD="\"${ELASTIC_PASSWORD}\"" > .env
podman exec -it elastic_cont bash -c "cp -ar /usr/share/elasticsearch/config/certs/* /etc/certs"
podman stop elastic_cont
podman start elastic_cont
