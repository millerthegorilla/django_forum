import logging
from collections import namedtuple
from datetime import datetime, timedelta, timezone

from crispy_bootstrap5 import bootstrap5
from crispy_forms import helper, layout
from django import forms, shortcuts, utils
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import CharField
from django_messages import forms as messages_forms
from django_profile import forms as forum_forms
from tinymce.widgets import TinyMCE

from . import models as forum_models

logger = logging.getLogger(__name__)

User = get_user_model()


def validate_username(self, *args, **kwargs):
    breakpoint()
    pass


class UsernameField(CharField):
    default_validators = [validate_username]

    def clean(self, *args, **kwargs):
        return args[0]


# START FORUMPROFILE
# class AvatarForm(forms.Form):
#     def __init__(*args, **kwargs):


# this class is here to provide the user's forum profile
class ForumUserProfile(forum_forms.UserProfile):
    # model = get_user_model()
    username = UsernameField()

    class Meta(forum_forms.UserProfile.Meta):
        model = forum_forms.UserProfile.Meta.model
        exclude = forum_forms.UserProfile.Meta.exclude

    # def clean(self, *args, **kwargs):
    #     breakpoint()
    #     pass

    def __init__(self, *args, **kwargs) -> None:
        # I want the field 'display_name' to be placed above the user fields
        # TODO migrate display_name to django_artisan...?
        super().__init__(*args, **kwargs)
        try:
            initl = self.Meta.model.objects.get(
                username=self["username"].value()
            ).profile.display_name
        except self.Meta.model.DoesNotExist:
            initl = ""
        self.fields["display_name"] = forms.CharField(
            help_text="Your display name is used in the forum, and to make \
                        your personal page address.  Try your first name and last name, \
                        or use your business name.  It *must* be different to your username.  It will be \
                        converted to an internet friendly name when you save it.",
            initial=initl,
        )
        self.helper.layout = layout.Layout(
            bootstrap5.FloatingField("display_name"), self.helper.layout
        )
        self.helper.form_tag = False

    # def clean_username(self) -> str:
    #     breakpoint()
    #     username = self.cleaned_data["username"]
    #     return username


class ForumProfile(forum_forms.Profile):
    class Meta(forum_forms.Profile.Meta):
        model = forum_models.ForumProfile
        fields = forum_forms.Profile.Meta.fields + [
            "address_line_1",
            "address_line_2",
            "city",
            "country",
            "postcode",
        ]
        exclude = ["profile_user"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            layout.HTML(
                '<span class="tinfo">Address details are only necessary if there is going to be mail for users</span>'
            ),
            layout.HTML(
                '<a id="address-btn" class="btn btn-primary mb-3 ms-3" data-bs-toggle="collapse" \
                     href="#collapseAddress" role="button" aria-expanded="false" \
                     aria-controls="collapseAddress">Address details</a><br>'
            ),
            layout.Div(
                bootstrap5.FloatingField("address_line_1"),
                bootstrap5.FloatingField("address_line_2"),
                bootstrap5.FloatingField("city"),
                bootstrap5.FloatingField("country"),
                bootstrap5.FloatingField("postcode"),
                css_class="collapse ps-3",
                id="collapseAddress",
            ),
        )
        self.helper.form_id = "id-profile-form"
        self.helper.form_method = "post"
        self.helper.form_class = "col-auto"
        self.helper.form_tag = False


# ENDPROFILE

# START POST AND COMMENTS

# inherited from message_forms.Message :
# @staticmethod
# def sanitize_text(text: str) -> utils.safestring.SafeString:
#     return utils.safestring.mark_safe(
#         bleach.clean(
#             html.unescape(text),
#             tags=conf.settings.ALLOWED_TAGS,
#             attributes=conf.settings.ATTRIBUTES,
#             css_sanitizer=conf.settings.CSS_SANITIZER,
#             strip=True,
#             strip_comments=True,
#         )
#     )


class Post(messages_forms.Message):
    text = forms.CharField(
        error_messages={
            "required": "A post needs some text!\nyou tried to submit a blank value -\
            reverted to previous entry..."
        },
        widget=TinyMCE(),
    )
    title = forms.CharField(
        error_messages={
            "required": "A post needs a title!\nYou tried to submit a blank value\nreverted to previous entry..."
        }
    )

    class Meta:
        model = forum_models.Post
        fields = ["text", "title"]
        widgets = {"text": TinyMCE()}

    def __init__(self, *args, user: User = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            post = self.Meta.model.objects.get(author=user)
        except self.Meta.model.DoesNotExist:  # pylint: disable=no-member
            post = None
        checked_string = ""
        if post and post.subscribed_users.filter(username=user.username).count():
            checked_string = "checked"
        checkbox_string = (
            '<input type="checkbox" id="subscribe_cb" name="subscribe" value="Subscribe" '  # noqa: E501
            + checked_string
            + '> <label for="subscribe_cb" class="tinfo">Subscribe to this post...</label><br>'  # noqa: E501
        )
        self.helper = helper.FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = shortcuts.reverse("django_forum:post_create_view")
        self.helper.form_id = "id-post-create-form"
        self.helper.form_class = "col-10 col-sm-10 col-md-8 mx-auto"
        self.helper.layout = layout.Layout(
            layout.Fieldset(
                "Create your post...",
                bootstrap5.FloatingField("title"),
                layout.Field("text", css_class="mb-3 post-create-form-text"),
                layout.HTML(
                    "<div class='font-italic mb-3 tinfo'>Maximum of 2000 characters."
                    "Click on word count to see how many characters you have used...</div>"  # noqa: E501
                ),
                layout.HTML(checkbox_string),
                layout.Submit("save", "Publish Post", css_class="col-auto mt-3 mb-3"),
            )
        )

    def clean_title(self) -> str:
        return self.sanitize_text(self.cleaned_data["title"])


class Comment(messages_forms.Message):
    text = forms.CharField(
        widget=forms.TextInput()
    )  # attrs={"autofocus": "autofocus"}))

    class Meta:
        model = forum_models.Comment
        fields = messages_forms.Message.Meta.fields

    def __init__(self, *args, **kwargs) -> None:
        # get user from uername stored in author field
        if "data" in kwargs:
            temp = kwargs["data"].copy()
            # avoid db access if possible
            if "instance" in kwargs and kwargs["instance"] is not None:
                temp["author"] = kwargs["instance"].author
            else:
                temp["author"] = User.objects.get(username=kwargs["data"]["author"])
            kwargs["data"] = temp
        super().__init__(*args, **kwargs)
        # self.auto_id = False
        self.helper.layout = layout.Layout(
            layout.Fieldset(
                '<h3 id="comment" class="comment-headline">Comment away...!</h3>',
                layout.Row(
                    layout.Column(
                        layout.Field(
                            "text", id="comment-text", css_class="comment-form-text"
                        ),
                        layout.Div(
                            layout.HTML("<span>...characters left: 500</span>"),
                            id="count",
                            css_class="ms-auto tinfo",
                        ),
                        css_class="d-flex flex-column",
                    ),
                    css_class="d-flex flex-row align-items-end",
                ),
                layout.Submit(
                    "save",
                    "comment",
                    css_id="submit-comment",
                    css_class="col-auto mt-3",
                ),
                css_class="tinfo",
            )
        )
        self.helper.form_id = "id-post-create-form"
        self.helper.form_method = "post"
        self.helper.form_class = "col-auto"


## TODO add choices field to search page
class PostListSearch(forms.Form):
    # date constants for search page published at dropdown, where each constant represents
    # a time range tuple (created_at__lt, created_at__gt)
    # in django_forum.views.py line 91
    # queryset = queryset.filter(created_at__lt=time_range[0], created_at__gt=time_range[1])
    date_end_of_last_month = datetime(
        utils.timezone.now().year, utils.timezone.now().month, 1
    ) - timedelta(1)
    DATE_ANY = 0
    DATE_TODAY = staticmethod(
        lambda: (
            utils.timezone.now(),
            datetime(
                utils.timezone.now().year,
                utils.timezone.now().month,
                utils.timezone.now().day,
                0,
                0,
                0,
            ),
        )
    )
    DATE_WEEK = staticmethod(
        lambda: (utils.timezone.now(), utils.timezone.now() - timedelta(7))
    )
    DATE_WEEK_LAST = staticmethod(
        lambda: (
            utils.timezone.now() - timedelta(7),
            utils.timezone.now() - timedelta(14),
        )
    )
    DATE_MONTH_LAST = staticmethod(
        lambda: (
            datetime(
                date_end_of_last_month.year,
                date_end_of_last_month.month,
                date_end_of_last_month.day,
                tzinfo=timezone.utc,
            ),
            datetime(
                date_end_of_last_month.year,
                date_end_of_last_month.month,
                1,
                tzinfo=timezone.utc,
            ),
        )
    )
    DATE_YEAR_NOW = staticmethod(
        lambda: (
            utils.timezone.now(),
            datetime(utils.timezone.now().year, 1, 1, tzinfo=timezone.utc),
        )
    )
    DATE_YEAR_LAST = staticmethod(
        lambda: (
            datetime(utils.timezone.now().year - 1, 12, 31, tzinfo=timezone.utc),
            datetime(utils.timezone.now().year - 1, 1, 1, tzinfo=timezone.utc),
        )
    )

    DATES = {}
    DATES["DATE_ANY"] = DATE_ANY
    DATES["DATE_TODAY"] = DATE_TODAY
    DATES["DATE_WEEK"] = DATE_WEEK
    DATES["DATE_WEEK_LAST"] = DATE_WEEK_LAST
    DATES["DATE_MONTH_LAST"] = DATE_MONTH_LAST
    DATES["DATE_YEAR_NOW"] = DATE_YEAR_NOW
    DATES["DATE_YEAR_LAST"] = DATE_YEAR_LAST

    # from dateparser import parse  TODO add search verbs to allow time phrases to be passed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    DATE_CHOICES = (
        ("DATE_ANY", "Any"),
        ("DATE_TODAY", "Today"),
        ("DATE_WEEK", "This week"),
        ("DATE_WEEK_LAST", "A week ago"),
        ("DATE_MONTH_LAST", "Last month"),
        ("DATE_YEAR_NOW", "This year"),
        ("DATE_YEAR_LAST", "Last year"),
    )

    q = forms.CharField(label="Search Query")
    published = forms.ChoiceField(
        choices=DATE_CHOICES, required=False, initial=DATE_ANY
    )

    class Meta:
        fields = []
        widgets = {"published": "select"}
