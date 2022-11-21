#!/bin/bash
if [[ -f /runserver.sh ]]
then
	rm /runserver.sh;
fi
ln -s /opt/ceramic_isles_test/django_forum/testapp/runserver.sh /runserver.sh
( python django_forum/testapp/manage.py qcluster ) &
#python -m pytest;
#exit 0
tail -f /dev/null