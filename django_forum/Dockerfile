# build command is: podman build --tag='python:django' -f='dockerfile_django'
FROM docker.io/library/python
ARG PROJECT_NAME="ceramic_isles_test"
ENV PYTHONPATH="/opt/${PROJECT_NAME}/"
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libmagic1 libmagickwand-dev libjpeg62-turbo-dev zlib1g-dev python3-pil python3-pil.imagetk graphviz graphviz-dev vim
RUN rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/${PROJECT_NAME};
RUN mkdir -p /var/log/${PROJECT_NAME};
COPY skel/* /etc/skel
RUN useradd -m artisan -s /bin/bash
RUN mkdir /home/artisan/django_venv
RUN chown artisan:artisan /opt/${PROJECT_NAME} /var/log/${PROJECT_NAME} /home/artisan/django_venv
ENV VIRTUAL_ENV=/home/artisan/django_venv
RUN su artisan -c "python3 -m venv $VIRTUAL_ENV"
# ENV PATH=$VIRTUAL_ENV/bin:$PATH
RUN touch /tmp/manage_output && chmod 0666 /tmp/manage_output
COPY ./pip_requirements /tmp/pip_requirements
RUN chmod o+r /tmp/pip_requirements
RUN su artisan -c ". /home/artisan/django_venv/bin/activate && python -m pip install --upgrade pip wheel && pip install --no-cache-dir -r /tmp/pip_requirements"
RUN rm -r /tmp/pip_requirements
#COPY ./docker_entrypoint_init.sh /docker_entrypoint_init.sh
# RUN chmod +x /docker_entrypoint_init.sh
# ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT ["/opt/ceramic_isles_test/django_forum/testapp/dockerfile_python/docker_entrypoint_init.sh"]