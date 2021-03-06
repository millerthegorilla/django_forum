from safe_imagefield.forms import SafeImageField    ## TODO: need to setup clamav.conf properly
from django.core.exceptions import ValidationError
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset, HTML, Div
from crispy_forms.helper import FormHelper
from crispy_bootstrap5.bootstrap5 import FloatingField

from django.conf import settings
from django import forms

from django_forum_app.forms import ForumProfileDetailForm

from .models import ArtisanForumProfile, UserProductImage
from .fields import FileClearInput, FileInput


MAX_NUMBER_OF_IMAGES = settings.MAX_USER_IMAGES


class ArtisanForumProfileDetailForm(ForumProfileDetailForm):
    image_file = SafeImageField(allowed_extensions=('jpg','png'), 
                               check_content_type=True, 
                               scan_viruses=True, 
                               media_integrity=True,
                               max_size_limit=2621440)

    class Meta(ForumProfileDetailForm.Meta):
        model = ArtisanForumProfile
        fields = ForumProfileDetailForm.Meta.fields + [
                                                  'image_file', \
                                                  'bio', \
                                                  'shop_web_address', \
                                                  'outlets', \
                                                  'listed_member', \
                                                  'display_personal_page', \
                                                 ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_file'].widget.is_required = False
        self.fields['image_file'].required = False
        self.fields['image_file'].help_text = '<span class="text-white">A single image for your personal page, click Update Profile to upload it...</span>'
        self.fields['bio'] = forms.fields.CharField(
                label="Biographical Information",
                help_text='<span class="text-white">Biographical detail is a maximum 500 character space to display \
                                     on your personal page.</span>',
                widget=forms.Textarea(),
                required=False)
        self.fields['shop_web_address'] = forms.fields.CharField(
                label='Your Online Shop Web Address',
                help_text='<span class="tinfo">Your shop web address to be displayed on your personal page</span>',
                required=False)
        self.fields['outlets'] = forms.fields.CharField(
                label='Outlets that sell your wares',
                help_text='<span class="tinfo">A comma separated list of outlets that sell your stuff, for your personal page.</span>',
                required=False)
        # add to the super class fields
        self.helper.layout.fields = self.helper.layout.fields + [ 
            FileClearInput('image_file', css_class="tinfo form-control form-control-lg"),
            FloatingField('bio'),
            FloatingField('shop_web_address'),
            FloatingField('outlets'),
            Div(Field('listed_member'), css_class="tinfo"),
            Div(Field('display_personal_page'), css_class="tinfo"),
        ]
        self.helper.form_id = 'id-profile-form'
        self.helper.form_method = 'post'
        self.helper.form_class = 'col-auto tinfo'


class UserProductImageForm(forms.ModelForm):
    image_file = SafeImageField(allowed_extensions=('jpg','png'), 
                               check_content_type=True, 
                               scan_viruses=True, 
                               media_integrity=True,
                               max_size_limit=2621440)
    class Meta:
        model = UserProductImage
        fields = ['image_file', 'image_title', 'image_text', 'image_shop_link', 'image_shop_link_title']

    def __init__(self, instance=None, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['image_file'].validators.append(self.restrict_amount)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                FileInput('image_file', name="image_file"),
                FloatingField('image_title'),
                FloatingField('image_text'),
                FloatingField('image_shop_link'),
                FloatingField('image_shop_link_title'),),
        )
        self.helper.form_id = 'id-upload-form'
        self.helper.form_method = 'post'
        self.helper.form_class = 'col-auto col-xs-3'


    def restrict_amount(self, value):
        if self.user is not None:
            if UserProductImage.objects.filter(user_profile=self.user.profile.forumprofile).count() >= MAX_NUMBER_OF_IMAGES:
                raise ValidationError('User already has {} images'.format(MAX_NUMBER_OF_IMAGES))


# handles deletion
class UserProductImagesForm(forms.ModelForm):
    image_file = SafeImageField(allowed_extensions=('jpg','png'), 
                               check_content_type=True, 
                               scan_viruses=True, 
                               media_integrity=True,
                               max_size_limit=2621440)
    class Meta:
        model = UserProductImage
        fields = ['image_file', 'image_text', 'image_shop_link']
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['image_file'].validators.append(self.restrict_amount)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                FileInput('image_file', css_class="col-auto"),
                FloatingField('image_text', css_class="col-auto"),
                FloatingField('image_shop_link', css_class="col-auto"),),        
        )
        self.helper.form_id = 'id-upload-form'
        self.helper.form_method = 'post'
        self.helper.form_class = 'col-12'


    def restrict_amount(self, value):
        if self.user is not None:
            if UserProductImage.objects.filter(user_profile=self.user.profile.forumprofile).count() >= MAX_NUMBER_OF_IMAGES:
                raise ValidationError(_('User already has {0} images'.format(MAX_NUMBER_OF_IMAGES)),
                                      code='max_image_limit',
                                      params={'value':'3'})

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()