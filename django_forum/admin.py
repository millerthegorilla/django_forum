import logging

from django import conf, http, urls, utils
from django.apps import apps
from django.contrib import admin, messages
from django.db import models as db_models
from django_messages import soft_deletion
from django_profile import models as profile_models

from . import models as forum_models

logger = logging.getLogger("django_artisan")

try:
    abs_post = conf.settings.ABSTRACTPOST
except AttributeError:
    abs_post = False
if abs_post:
    try:
        post_model = apps.get_model(*conf.settings.POST_MODEL.split("."))
    except Exception:
        post_model = forum_models.Post
else:
    post_model = forum_models.Post

try:
    abs_comment = conf.settings.ABSTRACTCOMMENT
except AttributeError:
    abs_comment = False
ap = ""
if not abs_comment:
    comment_model = forum_models.Comment
else:
    try:
        comment_model = apps.get_model(*conf.settings.COMMENT_MODEL.split("."))
    except Exception:
        comment_model = forum_models.Comment
try:
    abs_post = conf.settings.ABSTRACTPOST
except AttributeError:
    abs_post = False

if abs_post:
    ap = conf.settings.POST_MODEL.split(".")[0]
else:
    ap = "django_forum"


@admin.register(post_model)
class Post(soft_deletion.Admin):
    """Post admin class

    Args:
        soft_deletion.Admin: an abstract class from django_messages that
                             allows posts etc to be soft deleted, and hard
                             deleted according to a schedule set in settings.py
    """

    list_display = (
        "commenting_locked",
        "pinned",
        "moderation_date",
        "active",
        "deleted_at",
        "author",
        "title",
        "text",
        "created_at",
    )
    list_filter = (
        "commenting_locked",
        "pinned",
        "moderation_date",
        "active",
        "created_at",
        "author",
        "deleted_at",
    )
    search_fields = ("author", "text", "title")

    actions = [
        "approve_post",
        "lock_commenting",
        "unlock_commenting",
        "unpin_post",
        "pin_post",
        "hard_delete_post",
    ]

    def approve_post(
        self, request: http.HttpRequest, queryset: db_models.QuerySet
    ) -> None:
        idx = 0
        for q in queryset:
            q.moderation_date = None
            q.commenting_locked = False
            try:
                q.save(update_fields=["moderation_date", "commenting_locked"])
                idx += 1
            except Exception as _e:
                logger.error("Error approving moderation : {0}".format(_e))

        self.message_user(
            request,
            utils.translation.ngettext(
                "%d post was approved.",
                "%d posts were approved.",
                idx,
            )
            % idx,
            messages.SUCCESS,
        )

    def lock_commenting(
        self, request: http.HttpRequest, queryset: db_models.QuerySet
    ) -> None:
        """_summary_

        Args:
            request (http.HttpRequest): _description_
            queryset (db_models.QuerySet): _description_
        """
        idx = 0
        for q in queryset:
            q.commenting_locked = True
            try:
                q.save(update_fields=["commenting_locked"])
                idx += 1
            except Exception as e:
                logger.error("Error locking comments : {0}".format(e))

        self.message_user(
            request,
            utils.translation.ngettext(
                "commenting on %d post was locked.",
                "commenting on %d posts was locked.",
                idx,
            )
            % idx,
            messages.SUCCESS,
        )

    def unlock_commenting(
        self, request: http.HttpRequest, queryset: db_models.QuerySet
    ) -> None:
        idx = 0
        for q in queryset:
            q.commenting_locked = False
            try:
                q.save(update_fields=["commenting_locked"])
                idx += 1
            except Exception as e:
                logger.error("Error unlocking comments : {0}".format(e))

        self.message_user(
            request,
            utils.translation.ngettext(
                "commenting on %d post was unlocked.",
                "commenting on %d posts was unlocked.",
                idx,
            )
            % idx,
            messages.SUCCESS,
        )

    def pin_post(self, request: http.HttpRequest, queryset: db_models.QuerySet) -> None:
        idx = 0
        for q in queryset:
            q.pinned = 1
            try:
                q.save(update_fields=["pinned"])
                idx += 1
            except Exception as e:
                logger.error("Error unpinning posts: {0}".format(e))

        self.message_user(
            request,
            utils.translation.ngettext(
                "%d post was unpinned.",
                "%d posts were unpinned.",
                idx,
            )
            % idx,
            messages.SUCCESS,
        )

    def unpin_post(
        self, request: http.HttpRequest, queryset: db_models.QuerySet
    ) -> None:
        idx = 0
        for q in queryset:
            q.pinned = 0
            try:
                q.save(update_fields=["pinned"])
                idx += 1
            except Exception as e:
                logger.error("Error unpinning posts: {0}".format(e))

        self.message_user(
            request,
            utils.translation.ngettext(
                "%d post was unpinned.",
                "%d posts were unpinned.",
                idx,
            )
            % idx,
            messages.SUCCESS,
        )

    def hard_delete_post(
        self, request: http.HttpRequest, queryset: db_models.QuerySet
    ) -> None:
        idx = 0
        for q in queryset:
            q.hard_delete()
            idx += 1

        self.message_user(
            request,
            utils.translation.ngettext(
                "%d post was deleted.",
                "%d posts were deleted.",
                idx,
            )
            % idx,
            messages.SUCCESS,
        )


try:
    abs_forum_profile = conf.settings.ABSTRACTFORUMPROFILE
except AttributeError:
    abs_forum_profile = False
if not abs_forum_profile:
    if not conf.settings.ABSTRACTPROFILE:
        admin.site.unregister(profile_models.Profile)

    @admin.register(forum_models.ForumProfile)
    class ForumProfile(admin.ModelAdmin):
        list_display = [
            "display_name",
            "address_line_1",
            "address_line_2",
            "city",
            "country",
            "postcode",
            "avatar",
            "rules_agreed",
        ]
        list_filter = ["display_name", "city", "country", "postcode", "rules_agreed"]
        search_fields = ["display_name", "address_line_1"]

        def get_queryset(self, request: http.HttpRequest) -> db_models.QuerySet:
            return (
                super().get_queryset(request).exclude(profile_user__is_superuser=True)
            )


@admin.register(comment_model)
class Comment(soft_deletion.Admin):
    # fields = ('moderation', 'active', 'author', 'title', 'text', 'created_at', 'deleted_at', 'user_profile') # noqa: E501
    # fieldsets = [
    #     ('Moderation', {'fields': ['moderation']}),
    #     ('Active', {'fields': ['active']}),
    #     ('Author', {'fields': ['author']}),
    #     ('Text', {'fields': ['text']}),
    # ]
    list_display = (
        "moderation_date",
        "active",
        "post_str",
        "author",
        "text",
        "created_at",
        "deleted_at",
    )
    list_editable = ("text",)
    list_filter = (
        "moderation_date",
        "active",
        "created_at",
        "post_fk",
        "author",
        "deleted_at",
    )
    search_fields = ("author", "text")

    def post_str(self, obj: forum_models.Comment) -> str:
        global ap
        link = urls.reverse("admin:" + ap + "_post_change", args=[obj.post_fk.id])
        return utils.safestring.mark_safe(
            f'<a href="{link}">{utils.html.escape(obj.post_fk.title)}</a>'
        )

    post_str.short_description = "Post"  # type: ignore
    # make row sortable
    post_str.admin_order_field = "post"  # type: ignore

    actions = [
        "approve_comment",
        "hard_delete_comment",
    ]

    def approve_comment(self, request: http.HttpRequest, queryset: db_models.QuerySet):
        updated = queryset.update(moderation_date=None)

        self.message_user(
            request,
            utils.translation.ngettext(
                "%d comment was approved.",
                "%d comments were approved.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    def hard_delete_comment(
        self, request: http.HttpRequest, queryset: db_models.QuerySet
    ) -> None:
        idx = 0
        for q in queryset:
            q.hard_delete()
            idx += 1

        self.message_user(
            request,
            utils.translation.ngettext(
                "%d comment was deleted.",
                "%d comments were deleted.",
                idx,
            )
            % idx,
            messages.SUCCESS,
        )
