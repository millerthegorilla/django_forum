import elasticsearch_dsl
import html
import logging
import uuid
import typing
import bleach

from django_q import tasks

from django import http, urls, shortcuts, views, utils, conf
from django.apps import apps
from django.core import mail
from django.core.cache import cache as template_cache
from django.core import paginator as pagination
from django.core.cache.utils import make_template_fragment_key
from django.contrib.auth import get_user_model
from django.contrib.auth import mixins
from django.template import defaultfilters
from django.views.decorators import cache
from django.views import generic
from django.utils import safestring


from django_messages import views as messages_views
from django_messages import forms as messages_forms

from . import documents as forum_documents
from . import models as forum_models
from . import forms as forum_forms

logger = logging.getLogger("django_artisan")


def send_mod_mail(type: str) -> None:
    mail.send_mail(
        "Moderation for {0}".format(type),
        "A {0} has been created and requires moderation.  Please visit the {1} \
        AdminPanel, and inspect the {0}".format(
            type, conf.settings.SITE_NAME
        ),
        conf.settings.EMAIL_HOST_USER,
        list(
            get_user_model()
            .objects.filter(is_staff=True)
            .values_list("email", flat=True)
        ),
        fail_silently=False,
    )


# START POSTS AND COMMENTS
class PostCreate(mixins.LoginRequiredMixin, generic.edit.CreateView):
    model = forum_models.Post
    template_name = "django_forum/posts_and_comments/forum_post_create_form.html"
    form_class = forum_forms.Post

    def get_context_data(self, form: forum_forms.Post = None):
        if form and "text" in form.errors.keys():
            form.errors["text"] = [
                "A post needs some text! - you tried to submit a blank value...  Try again :)"
            ]
        else:
            form = self.form_class()
        return {"form": form}

    def form_valid(self, form: forum_forms.Post) -> http.HttpResponseRedirect:
        post = form.save(commit=False)
        post.author = self.request.user
        if "subscribe" in self.request.POST:
            post.subscribed_users.add(self.request.user)
        post.save()
        return shortcuts.redirect(self.get_success_url(post))

    def get_success_url(self, post: forum_models.Post, *args, **kwargs) -> str:
        return urls.reverse_lazy(
            "django_forum:post_view",
            args=(
                post.id,
                post.slug,
            ),
        )


@utils.decorators.method_decorator(cache.never_cache, name="dispatch")
class PostList(mixins.LoginRequiredMixin, generic.list.ListView):
    model = forum_models.Post
    template_name = "django_forum/posts_and_comments/forum_post_list.html"
    paginate_by = conf.settings.NUMPOSTS
    """
       the documentation for django-elasticsearch and elasticsearch-py
       as well as elasticsearch is not particularly good, at least not in my experience.
       The following searches posts and comments.  The search indexes are defined in
       documents.py.
    """

    def get(self, request: http.HttpRequest) -> typing.Union[tuple, http.HttpResponse]:
        """
        I had a function that tested for the existence of a search slug
        and then performed the search if necessary.  I have refactored that
        to the below, that uses duck typing (type coercion) to perform the
        logic of the search.  It is probably a lot slower, but seems more pythonic.
        So, TODO profile this method vs the original from commit id
        1d5cbccde9f7b183e4d886d7e644712b79db60cd
        """
        # site = site_models.Site.objects.get_current()
        search = 0
        p_c = None
        is_a_search = False
        form = forum_forms.PostListSearch(request.GET)
        if form.is_valid():
            is_a_search = True
            terms = form.cleaned_data["q"].split(" ")
            if len(terms) > 1:
                t = "terms"
            else:
                t = "match"
                terms = terms[0]
            queryset = (
                forum_documents.Post.search()
                .query(
                    elasticsearch_dsl.Q(t, text=terms)
                    | elasticsearch_dsl.Q(t, author=terms)
                    | elasticsearch_dsl.Q(t, title=terms)
                )
                .to_queryset()
            )
            queryset_comments = (
                forum_documents.Comment.search()
                .query(
                    elasticsearch_dsl.Q(t, text=terms)
                    | elasticsearch_dsl.Q(t, author=terms)
                )
                .to_queryset()
            )
            for sr in queryset_comments:
                queryset = queryset | self.model.objects.filter(id=sr.post_fk.id)
            time_range = form.DATES[form["published"].value()]()
            search = len(queryset)
            if search and time_range:
                queryset = (
                    queryset.filter(
                        created_at__lt=time_range[0], created_at__gt=time_range[1]
                    )
                    .order_by("-pinned")
                    .select_related("author")
                    .select_related("author__profile")
                    .select_related("author__profile__avatar")
                )
                search = len(queryset)
            if not search:
                queryset = (
                    self.model.objects.order_by("-pinned")
                    .select_related("author")
                    .select_related("author__profile")
                    .select_related("author__profile__avatar")
                )
        else:
            form.errors.clear()
            queryset = (
                self.model.objects.order_by("-pinned")
                .select_related("author")
                .select_related("author__profile")
                .select_related("author__profile__avatar")
            )
        paginator = pagination.Paginator(queryset, self.paginate_by)

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {
            "form": form,
            "page_obj": page_obj,
            "search": search,
            "is_a_search": is_a_search,
            "site_url": (request.scheme or "https") + "://" + request.get_host(),
        }
        return shortcuts.render(request, self.template_name, context)


@utils.decorators.method_decorator(cache.never_cache, name="dispatch")
@utils.decorators.method_decorator(cache.never_cache, name="get")
class PostView(mixins.LoginRequiredMixin, generic.DetailView):
    model: forum_models.Post = forum_models.Post
    template_name: str = "django_forum/posts_and_comments/forum_post_detail.html"
    form_class: forum_forms.Post = forum_forms.Post
    comment_form_class: forum_forms.Comment = forum_forms.Comment

    def get(self, request: http.HttpRequest, pk: int, slug: str) -> http.HttpResponse:
        self.object = self.get_object(
            queryset=self.model.objects.select_related("author")
            .select_related("author__profile")
            .select_related("author__profile__avatar")
        )
        context = self.get_context_data(request=request)
        return shortcuts.render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        request = kwargs["request"]
        context_data = {}
        context_data["post"] = self.object
        context_data["title_errors"] = ""
        context_data["text_errors"] = ""
        context_data["site_url"] = (
            (request.scheme or "https") + "://" + conf.settings.SITE_DOMAIN
        )
        context_data["comment_form"] = self.comment_form_class()  # type: ignore
        context_data["subscribed"] = (
            context_data["post"]
            .subscribed_users.filter(username=self.request.user.username)
            .count()
        )
        context_data["comments"] = (
            self.object.comments.all()
            .select_related("author")
            .select_related("author__profile")
            .select_related("author__profile__avatar")
        )
        return context_data


# ajax function for subscribe checkbox
def subscribe(request) -> http.JsonResponse:
    if conf.settings.ABSTRACTPOST:
        post_model = apps.get_model(*conf.settings.POST_MODEL.split("."))
    else:
        post_model = forum_models.Post
    # request should be ajax and method should be POST.
    if (
        request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        fp = post_model.objects.prefetch_related("subscribed_users").get(
            slug=request.POST["slug"]
        )
        if request.POST["data"] == "true":
            fp.subscribed_users.add(request.user)
        else:
            fp.subscribed_users.remove(request.user)
        return http.JsonResponse({}, status=200)
    else:
        return http.JsonResponse({"error": ""}, status=500)


class PostUpdate(mixins.LoginRequiredMixin, generic.UpdateView):
    model = forum_models.Post
    a_name = "django_forum"
    form_class = forum_forms.Post
    comment_form_class = forum_forms.Comment
    template_name = "django_forum/posts_and_comments/forum_post_detail.html"

    def form_invalid(self, form):
        context_data = {
            "form": form,
            "text_errors": form.errors.get("text", ""),
            "title_errors": form.errors.get("title", ""),
        }
        breakpoint()
        context_data["post"] = self.object
        context_data["comments"] = (
            self.object.comments.all()
            .select_related("author")
            .select_related("author__profile")
            .select_related("author__profile__avatar")
        )
        context_data["comment_form"] = self.comment_form_class()
        return shortcuts.render(
            self.request, self.template_name, context_data, status=406
        )

    def form_valid(self, form):
        post = form.save()
        return http.JsonResponse({"url": post.get_absolute_url()}, status=200)


class DeletePost(mixins.LoginRequiredMixin, views.View):
    http_method_names = ["post"]
    model = forum_models.Post
    a_name = "django_forum"

    def post(
        self, request: http.HttpRequest, pk: int, slug: str
    ) -> http.HttpResponseRedirect:
        post = self.model.objects.get(id=pk, slug=slug)
        if post.author == request.user:
            try:
                post.delete()
            except self.model.DoesNotExist:
                logger.warn("the model you tried to delete does not exist")

        return shortcuts.redirect(urls.reverse_lazy(self.a_name + ":post_list_view"))


class CreateComment(mixins.LoginRequiredMixin, views.generic.CreateView):
    post_model: forum_models.Post = forum_models.Post
    model: forum_models.Comment = forum_models.Comment
    form_class: forum_forms.Comment = forum_forms.Comment
    post_form_class: forum_forms.Post = forum_forms.Post
    template_name = "django_forum/posts_and_comments/forum_post_detail.html"

    def form_invalid(self, form):
        post = self.post_model.objects.get(
            pk=self.kwargs["pk"], slug=self.kwargs["slug"]
        )
        context_data = {"form": self.post_form_class(instance=post)}
        context_data["post"] = post
        context_data["comments"] = (
            post.comments.all()
            .select_related("author")
            .select_related("author__profile")
            .select_related("author__profile__avatar")
        )
        context_data["comment_form"] = form
        return shortcuts.render(self.request, self.template_name, context_data)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_fk = self.post_model.objects.get(id=self.kwargs["pk"])
        comment.slug = defaultfilters.slugify(
            comment.text[:4]
            + "_comment_"
            + str(comment.created_at or utils.timezone.now())
        )
        comment.save()
        sname: str = "subscribe_timeout" + str(uuid.uuid4())
        protocol = "https" if self.request.is_secure() else "http"
        domain = self.request.get_host()
        tasks.schedule(
            "django_forum.tasks.send_subscribed_email",
            self.post_model._meta.app_label + "." + self.post_model._meta.object_name,
            self.model._meta.app_label + "." + self.model._meta.object_name,
            name=sname,
            schedule_type="O",
            repeats=-1,
            next_run=utils.timezone.now() + conf.settings.COMMENT_WAIT,
            post_id=comment.post_fk.id,
            comment_id=comment.id,
            path=comment.get_absolute_url(),
            protocol=protocol,
            domain=domain,
            s_name=sname,
        )
        return shortcuts.redirect(
            urls.reverse(
                "django_forum:post_view", args=(self.kwargs["pk"], self.kwargs["slug"])
            ),
            permanent=True,
        )


class DeleteComment(mixins.LoginRequiredMixin, views.generic.DeleteView):
    model = forum_models.Comment

    def get_success_url(self, *args, **kwwargs):
        return (
            urls.reverse(
                "django_forum:post_view",
                args=(self.object.post_fk.id, self.object.post_fk.slug),
            )
            + "#thepost"
        )


class UpdateComment(mixins.LoginRequiredMixin, views.generic.UpdateView):
    model = forum_models.Comment
    form_class = forum_forms.Comment


class ReportComment(mixins.LoginRequiredMixin, views.View):
    http_method_names = ["post"]
    comment_model = forum_models.Comment
    post_model = forum_models.Post
    a_name = "django_forum"

    def post(self, request: http.HttpRequest) -> http.HttpResponseRedirect:
        comment = self.comment_model.objects.get(
            id=request.POST["comment-id"], slug=request.POST["comment-slug"]
        )
        post = self.post_model.objects.get(
            id=request.POST["post-id"], slug=request.POST["post-slug"]
        )
        if comment.author != request.user:
            comment.moderation_date = utils.timezone.now()
            comment.save(update_fields=["moderation_date"])
            tasks.async_task("django_forum.tasks.send_mod_mail", type="Comment")
        return shortcuts.redirect(
            urls.reverse_lazy(self.a_name + ":post_view", args=[post.id, post.slug])
            + "#"
            + comment.slug
        )


class ReportPost(mixins.LoginRequiredMixin, views.View):
    http_method_names = ["post"]
    post_model = forum_models.Post
    a_name = "django_forum"

    def post(self, request: http.HttpRequest) -> http.HttpResponseRedirect:
        post = self.post_model.objects.get(
            id=request.POST["post-id"], slug=request.POST["post-slug"]
        )
        if post.author != request.user:
            post.moderation_date = utils.timezone.now()
            post.commenting_locked = True
            post.save(update_fields=["moderation_date", "commenting_locked"])
            tasks.async_task("django_forum.tasks.send_mod_mail", "Post")
        return shortcuts.redirect(
            urls.reverse_lazy(self.a_name + ":post_view", args=[post.id, post.slug])
        )
