import logging
from collections import namedtuple
from datetime import datetime, timedelta, timezone

from crispy_forms import helper, layout
from crispy_bootstrap5 import bootstrap5
from tinymce.widgets import TinyMCE
from tinymce import models as tinymce_models

from django import forms, utils, shortcuts
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings

from django_profile import forms as profile_forms
from django_messages import forms as messages_forms

from . import models as forum_models


from django.forms import CharField

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
class ForumProfileUser(profile_forms.UserProfile):
    # model = get_user_model()
    username = UsernameField()

    class Meta(profile_forms.UserProfile.Meta):
        model = profile_forms.UserProfile.Meta.model
        exclude = profile_forms.UserProfile.Meta.exclude

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


class ForumProfile(profile_forms.Profile):
    class Meta(profile_forms.Profile.Meta):
        model = forum_models.ForumProfile
        fields = profile_forms.Profile.Meta.fields + [
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
                '<a class="btn btn-primary mb-3 ms-3" data-bs-toggle="collapse" \
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


class PostCreate(messages_forms.Message):
    text = forms.CharField(
        error_messages={"required": "A post needs some text!"},
        widget=TinyMCE(),
    )
    title = forms.CharField(error_messages={"required": "A post needs a title!"})

    class Meta(messages_forms.Message.Meta):
        model = forum_models.Post
        fields = ["text", "title"]
        widgets = {"text": TinyMCE()}

    def __init__(self, user: User = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        checked_string = ""
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

    def clean_text(self) -> str:
        return self.sanitize_text(self.cleaned_data["text"])


class PostUpdate(messages_forms.Message):
    text = forms.CharField(
        error_messages={"required": "A post needs some text!"},
        widget=TinyMCE(
            attrs={"required": "true", "readonly": ""},
            mce_attrs={
                "selector": "#tinymce-text",
                "init_instance_callback": "onInstanceInit",
            },
        ),
    )

    title = forms.CharField(error_messages={"required": "A post needs a title!"})

    class Meta:
        model = forum_models.Post
        fields = ["title"]
        # widgets = {"text": TinyMCE(attrs={"init_instance_callback": "onInstanceInit"})}

    # def clean(self):
    #     breakpoint()
    #     if self["text"].value() == "":
    #         self.cleaned_data["text"] = self.initial["text"]
    #         self.data = self.data.copy()
    #         self.data["text"] = self.initial["text"]

    #     return self.cleaned_data

    # def clean_text(self):
    #     breakpoint()
    #     super().clean_text()
    #     if self.cleaned_data["text"] == "":
    #         return self.initial["text"]

    def __init__(self, editable=True, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        checked_string = ""

        self.fields["text"].initial = self.sanitize_text(self.instance.text)
        if self.instance and self.instance.subscribed_users.count():
            checked_string = "checked"
        checkbox_string = (
            '<input type="checkbox" id="subscribe_cb" name="subscribe" value="Subscribe" '  # noqa: E501
            + checked_string
            + '> <label for="subscribe_cb" class="tinfo">Subscribe to this post...</label><br>'  # noqa: E501
        )
        self.helper = helper.FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-horizontal"
        self.helper.form_show_labels = False
        self.helper.form_action = shortcuts.reverse(
            "django_forum:post_update", args=(self.instance.id, self.instance.slug)
        )
        self.helper.form_id = "id-post-update-form"
        self.helper.form_class = "col-10 col-sm-10 col-md-8 mx-auto"
        if self.instance.moderation_date:
            text = layout.HTML(
                "<div>This post has been reported and is awaiting moderation.  Comments are locked until the post has been validated.</div>"  # noqa: E501
            )
        if editable:
            text = layout.Field("text", id="tinymce-text")
            edit_buttons = layout.HTML(
                '<div class="ms-auto"> \
                    <div class="post-edit-div"> \
                        <div class="mt-3"> \
                            <button id="editor-cancel-btn" type="button" class="ms-auto col-auto btn btn-secondary me-2">Cancel</button> \
                            <button id="editor-submit-btn" type="submit" class="me-auto col-auto btn btn-primary">Save Post</button> \
                        </div> \
                    </div> \
                </div>'
            )
        else:
            text = layout.Div("text", id="tinymce-text")
            edit_buttons = layout.HTML("")

        self.helper.layout = layout.Layout(
            layout.Div(
                layout.Field(
                    "title",
                    id="title-input",
                    wrapper_class="post-title-wrapper",
                    css_class="post-title flex-fill post-headline",
                ),
                layout.HTML("by {{post.author}} at {{post.created_at}}"),
                text,
                layout.HTML("<div id='text-div'></div>"),
                edit_buttons,
                layout.HTML(checkbox_string),
                css_class="d-flex flex-column",
            ),
        )

    def clean(self):
        breakpoint()
        return super().clean()


class PostModeration(forms.Form):
    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-horizontal"
        self.helper.form_show_labels = False
        self.helper.form_action = shortcuts.reverse(
            "django_forum:post_report", args=(instance.id, instance.slug)
        )
        self.helper.form_id = "id-post-update-form"
        self.helper.form_class = "col-10 col-sm-10 col-md-8 mx-auto"
        self.helper.layout = layout.Layout(
            layout.Submit("submit", "Report Post for Moderation")
        )


class Comment(messages_forms.Message):
    text = forms.CharField(widget=forms.TextInput(attrs={"autofocus": "autofocus"}))

    class Meta:
        model = forum_models.Comment
        fields = messages_forms.Message.Meta.fields

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # self.auto_id = False
        self.helper.layout = layout.Layout(
            layout.Fieldset(
                '<h3 id="comment" class="comment-headline">Comment away...!</h3>',
                layout.Row(
                    layout.Column(
                        layout.Field("text", css_class="comment-form-text"),
                        layout.Div(
                            layout.HTML("<span>...characters left: 500</span>"),
                            id="count",
                            css_class="ms-auto tinfo",
                        ),
                        css_class="d-flex flex-column",
                    ),
                    css_class="d-flex flex-row align-items-end",
                ),
                layout.Submit("save", "comment", css_class="col-auto mt-3"),
                css_class="tinfo",
            )
        )
        self.helper.form_id = "id-post-create-form"
        self.helper.form_method = "post"
        self.helper.form_class = "col-auto"

    # def clean_text(self) -> str:
    #     breakpoint()
    #     if self.cleaned_data["text"] and not self.sanitize_text(
    #         self.cleaned_data["text"]
    #     ):
    #         if "text" in self.errors and type(self.errors["text"]) == list:
    #             self.errors["text"].append("That is not allowed here")
    #         else:
    #             self.errors["text"] = [
    #                 self.errors["text"] if "text" in self.errors else "",
    #                 "That is not allowed here",
    #             ]
    #     return self.cleaned_data['text']


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
    DATE_TODAY = (
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
    DATE_WEEK = (utils.timezone.now(), utils.timezone.now() - timedelta(7))
    DATE_WEEK_LAST = (
        utils.timezone.now() - timedelta(7),
        utils.timezone.now() - timedelta(14),
    )
    DATE_MONTH_LAST = (
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
    DATE_YEAR_NOW = (
        utils.timezone.now(),
        datetime(utils.timezone.now().year, 1, 1, tzinfo=timezone.utc),
    )
    DATE_YEAR_LAST = (
        datetime(utils.timezone.now().year - 1, 12, 31, tzinfo=timezone.utc),
        datetime(utils.timezone.now().year - 1, 1, 1, tzinfo=timezone.utc),
    )

    # from dateparser import parse  TODO add search verbs to allow time phrases to be passed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.DATES = {}
        self.DATES["DATE_ANY"] = self.DATE_ANY
        self.DATES["DATE_TODAY"] = self.DATE_TODAY
        self.DATES["DATE_WEEK"] = self.DATE_WEEK
        self.DATES["DATE_WEEK_LAST"] = self.DATE_WEEK_LAST
        self.DATES["DATE_MONTH_LAST"] = self.DATE_MONTH_LAST
        self.DATES["DATE_YEAR_NOW"] = self.DATE_YEAR_NOW
        self.DATES["DATE_YEAR_LAST"] = self.DATE_YEAR_LAST

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
