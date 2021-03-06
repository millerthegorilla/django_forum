from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset, HTML, Div
from crispy_bootstrap5.bootstrap5 import FloatingField

from tinymce.widgets import TinyMCE

from django_profile.forms import ProfileUserForm, ProfileDetailForm
from django_posts_and_comments.forms import PostCreateForm, CommentForm
from .models import ForumProfile, ForumPost, ForumComment
from .fields import FileInput


### START FORUMPROFILE
# class AvatarForm(forms.Form):
#     def __init__(*args, **kwargs):
        

class ForumProfileUserForm(ProfileUserForm):
    class Meta(ProfileUserForm.Meta):
        fields = ProfileUserForm.Meta.fields
        model = ProfileUserForm.Meta.model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(args):
            initl = args[0].get('display_name')
        else:
            initl = ForumProfile.objects.get(profile_user__username= kwargs['initial']['username']).display_name
        self.fields['display_name'] = forms.CharField(
            help_text='<span class="tinfo">Your display name is used in the forum, and to make \
                        your personal page address.  Try your first name and last name, \
                        or use your business name.  It *must* be different to your username.  It will be \
                        converted to an internet friendly name when you save it.</span>',
            initial=initl)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            FloatingField('display_name'),
            self.helper.layout)


class ForumProfileDetailForm(ProfileDetailForm):
    class Meta(ProfileDetailForm.Meta):
        model = ForumProfile
        fields = ProfileDetailForm.Meta.fields + [
                                                  'address_line_1', \
                                                  'address_line_2', \
                                                  'parish', \
                                                  'postcode', \
                                                 ]
        exclude = ['profile_user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
                HTML('<span class="tinfo">Address details are only necessary if there is going to be mail for users</span>'),
                HTML('<a class="btn btn-primary mb-3 ms-3" data-bs-toggle="collapse" \
                     href="#collapseAddress" role="button" aria-expanded="false" \
                     aria-controls="collapseAddress">Address details</a><br>'),
                Div(
                FloatingField('address_line_1'),
                FloatingField('address_line_2'),
                FloatingField('parish'),
                FloatingField('postcode'),
                css_class="collapse ps-3", id="collapseAddress"),
        )
        self.helper.form_id = 'id-profile-form'
        self.helper.form_method = 'post'
        self.helper.form_class = 'col-auto'


###  ENDPROFILE

###  START POST AND COMMENTS

class ForumPostCreateForm(PostCreateForm):
    class Meta(PostCreateForm.Meta):
        model = ForumPost
        fields = PostCreateForm.Meta.fields + ['category', 'location']
        widgets = { 'text': TinyMCE() }
        labels = { 'category':'Choose a category for your post...', 'location':'Which island...?'}

    def __init__(self, user_name=None, post=None, **kwargs):
        checked_string = ''
        super().__init__(**kwargs)
        if post and user_name and post.subscribed_users.filter(username=user_name).count():
            checked_string='checked'
        checkbox_string = '<input type="checkbox" id="subscribe_cb" name="subscribe" value="Subscribe" ' + checked_string + '> \
                              <label for="subscribe_cb" class="tinfo">Subscribe to this post...</label><br>'
        self.helper.layout = Layout(
            Fieldset(
                'Create your post...',
                FloatingField('title'),
                Field('text', css_class="mb-3 post-create-form-text"),
                HTML("<div class='font-italic mb-3 tinfo'>Maximum of 2000 characters.  Click on word count to see how many characters you have used...</div>"),
                Div(Field('category', css_class="col-auto"), Field('location', css_class="col-auto"), css_class="col-8 col-sm-4 col-md-4 col-lg-3 tinfo"),
                HTML(checkbox_string),
                Submit('save', 'Publish Post', css_class="col-auto mt-3 mb-3"),
            )
        )
        self.helper.form_action = 'django_forum_app:post_create_view'


class ForumCommentForm(CommentForm):
    class Meta:
        model = ForumComment
        fields = CommentForm.Meta.fields + []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                '<h3 class="comment-headline">Comment away...!</h3>',
                Row(
                    Column(
                        Field('text', css_class="comment-form-text"),
                        Div(HTML('<span>...characters left: 500</span>'), 
                            id="count", css_class="ms-auto tinfo"),
                               css_class="d-flex flex-column"),
                        css_class="d-flex flex-row align-items-end"),
                Submit('save', 'comment', css_class="col-auto mt-3"),
            css_class="tinfo")
        )
        self.helper.form_id = 'id-post-create-form'
        self.helper.form_method = 'post'
        self.helper.form_class = 'col-auto'
        self.helper.form_action = 'django_forum_app:post_view'


class ForumPostListSearch(forms.Form):
    PUBLISHED_ANY = ''
    PUBLISHED_TODAY = '1'
    PUBLISHED_WEEK = '7'

    PUBLISHED_CHOICES = (
        (PUBLISHED_ANY, 'Any'),
        (PUBLISHED_TODAY, 'Today'),
        (PUBLISHED_WEEK, 'This week'),
    )

    q = forms.CharField(label='Search Query')
    published = forms.ChoiceField(choices=PUBLISHED_CHOICES, required=False, initial=PUBLISHED_ANY)
