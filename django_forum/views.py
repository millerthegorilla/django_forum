import logging

from django_email_verification import send_email

from django import http, utils, urls, conf, shortcuts
from django.core import paginator as pagination
from django.contrib.auth import mixins
from django.template import defaultfilters
from django.views.decorators import cache
from django.views import generic
from django.forms.models import model_to_dict

from django_profile import views as profile_views

from . import models as forum_models
from . import forms as forum_forms
from . import forms_custom_registration as custom_reg_form

logger = logging.getLogger(__name__)


# START PROFILE


class UpdateAvatar(mixins.LoginRequiredMixin, generic.edit.UpdateView):
    model = forum_models.ForumProfile
    success_url = urls.reverse_lazy("django_forum:profile_update_view")

    def post(self, request: http.HttpRequest):
        fp = self.model.objects.get(profile_user=request.user)
        fp.avatar.image_file.save(request.FILES["avatar"].name, request.FILES["avatar"])
        return shortcuts.redirect(self.success_url)


@utils.decorators.method_decorator(cache.never_cache, name="dispatch")
class ForumProfile(profile_views.ProfileUpdate):
    model = forum_models.ForumProfile
    post_model = forum_models.Post
    form_class = forum_forms.ForumProfile
    user_form_class = forum_forms.ForumUserProfile
    success_url = urls.reverse_lazy("django_forum:profile_update_view")
    template_name = "django_forum/profile/forum_profile_update_form.html"

    def post(self, request: http.HttpRequest):
        form = self.form_class(request.POST, initial=request.user.profile.__dict__)
        user_form = self.user_form_class(
            request.POST, initial=model_to_dict(request.user)
        )

        if len(user_form["username"].errors):
            user_form.errors["username"][:] = (
                value
                for value in user_form.errors["username"]
                if value != "A user with that username already exists."
            )
            if not len(user_form.errors["username"]):
                del user_form.errors["username"]

        if not form.errors and form.fields:
            pf = request.user.profile
            for x in form.changed_data:
                setattr(request.user.profile, x, form[x].value())
            if "display_name" in user_form.changed_data:
                pf.display_name = user_form["display_name"].value()
                form.changed_data.append("display_name")
            pf.save(update_fields=form.changed_data)

        if not user_form.errors:
            uf = user_form.save(commit=False)
            uf.id = request.user.id
            uf.save(
                update_fields=[
                    x for x in user_form.cleaned_data.keys() if x != "display_name"
                ]
            )

        if user_form.errors or form.errors:
            return shortcuts.render(
                request,
                self.template_name,
                context={
                    "avatar": self.model.objects.get(
                        profile_user=self.request.user
                    ).avatar,
                    "form": form,
                    "user_form": user_form,
                },
            )

        return shortcuts.redirect(self.success_url)

    def get_context_data(self, *args, **kwargs) -> dict:
        context = {}
        context["form"] = self.form_class(initial=self.request.user.profile.__dict__)
        context["user_form"] = self.user_form_class(
            initial=model_to_dict(self.request.user)
        )
        context["avatar"] = self.model.objects.get(
            profile_user=self.request.user
        ).avatar
        queryset = (
            self.post_model.objects.select_related("author")
            .select_related("author__profile")
            .filter(author=self.request.user)
        )
        paginator = pagination.Paginator(queryset, 6)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context


# END PROFILE

# NEEDED FOR ADDITION OF DISPLAY_NAME AND FORUM RULES
# the following goes in the project top level urls.py
# from django_forum.views import CustomRegister
# path('users/accounts/register/', CustomRegister.as_view(), name='register'),


class CustomRegister(generic.edit.CreateView):
    form_class = custom_reg_form.CustomUserCreation
    template_name = "django_users/register.html"
    success_url = urls.reverse_lazy("django_users:confirmation_sent")
    # success_url = shortcuts.reverse("django_users:password_reset_done")

    def form_valid(
        self, form: custom_reg_form.CustomUserCreation
    ) -> http.HttpResponseRedirect:
        user = form.save()  # creates profile
        user.profile.rules_agreed = form["rules"].value()
        user.profile.display_name = defaultfilters.slugify(form["display_name"].value())
        user.profile.save(update_fields=["rules_agreed", "display_name"])
        send_email(user)
        return shortcuts.redirect(self.success_url)


class RulesPageView(generic.base.TemplateView):
    template_name = "django_forum/rules.html"
    extra_context = {"app_name": conf.settings.SITE_NAME}
