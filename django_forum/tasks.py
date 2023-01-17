import logging
from typing import Type
import django_q

from django import conf
from django.apps import apps
from django.contrib.sites import models as site_models
from django.contrib import auth
from django.core import mail, exceptions
from django_forum.models import Post
from django_forum.models import Comment
from . import models as forum_models

logger = logging.getLogger("django_artisan")


def send_subscribed_email(
    post_mdl: str,
    comment_mdl: str,
    post_id: int,
    comment_id: int,
    path: str,
    protocol: str,
    domain: str,
    s_name: str,
) -> str:
    post = comment = None
    post_model = apps.get_model(*post_mdl.split("."))
    comment_model = apps.get_model(*comment_mdl.split("."))
    posts = post_model.objects.filter(id=post_id)
    if posts.exists():
        post = posts.first()

    comments = comment_model.objects.filter(id=comment_id)
    if comments.exists():
        comment = comments.first()

    if post and comment:
        if post.subscribed_users.exists():
            href = "{0}://{1}{2}".format(protocol, domain, path)

            email = mail.EmailMessage(
                "A new comment has been made at {}!".format(conf.settings.SITE_NAME),
                conf.settings.SUBSCRIBED_MSG.format(href),
                conf.settings.EMAIL_FROM_ADDRESS,
                ["subscribed_user@ceramicisles.org"],
                list(  # bcc
                    post.subscribed_users.all().values_list("email", flat=True)
                ),
                reply_to=[conf.settings.EMAIL_FROM_ADDRESS],
            )
            email.content_subtype = "html"
            email.send()
            return "Email Sent!"
    else:
        return "No Email Sent - either post or comment has been deleted..."

    #     try:
    #         schedule = django_q.models.Schedule.objects.get(name=s_name).delete()
    #     except exceptions.ObjectDoesNotExist as e:
    #         logger.error("Schedule doesn't exist : " + str(e))
    # remove scheduled job


def send_mod_mail(type: str) -> None:
    mail.send_mail(
        "Moderation for {0}".format(type),
        "A {0} has been created and requires moderation.  Please visit the {1} AdminPanel, and inspect the {0}".format(
            type, conf.settings.SITE_NAME
        ),
        conf.settings.EMAIL_HOST_USER,
        list(
            auth.get_user_model()
            .objects.filter(is_staff=True)
            .values_list("email", flat=True)
        ),
        fail_silently=False,
    )
