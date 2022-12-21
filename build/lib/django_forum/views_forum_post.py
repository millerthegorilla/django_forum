import elasticsearch_dsl
import html
import logging
import uuid
import typing
import bleach

from django_q import tasks

from django import http, shortcuts, urls, views, utils, conf
from django.apps import apps
from django.core import mail
from django.core.cache import cache as template_cache
from django.core import paginator as pagination
from django.core.cache.utils import make_template_fragment_key
from django.contrib import auth
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
            auth.get_user_model()
            .objects.filter(is_staff=True)
            .values_list("email", flat=True)
        ),
        fail_silently=False,
    )


# START POSTS AND COMMENTS
class PostCreate(auth.mixins.LoginRequiredMixin, generic.edit.CreateView):
    model = forum_models.Post
    template_name = "django_forum/posts_and_comments/forum_post_create_form.html"
    form_class = forum_forms.Post

    def get_context_data(self, form=None):
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
class PostList(auth.mixins.LoginRequiredMixin, generic.list.ListView):
    model = forum_models.Post
    template_name = "django_forum/posts_and_comments/forum_post_list.html"
    paginate_by = 5
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
            time_range = eval(
                "form." + form["published"].value()
            )  #### TODO !!! eval is evil.
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
        }  # site.domain}
        return shortcuts.render(request, self.template_name, context)


## autocomplete now removed to reduce number of requests
# def autocomplete(request):
#     max_items = 5
#     q = request.GET.get('q')
#     results = []
#     if q:
#         search = Post.search().suggest('results', q, term={'field':'text'})
#         result = search.execute()
#         for idx,item in enumerate(result.suggest['results'][0]['options']):
#             results.append(item.text)
#     return JsonResponse({
#         'results': results
#     })

# END POSTS AND COMMENTS


@utils.decorators.method_decorator(cache.never_cache, name="dispatch")
@utils.decorators.method_decorator(cache.never_cache, name="get")
class PostView(auth.mixins.LoginRequiredMixin, generic.DetailView):
    """
    TODO: Replace superclass form processing if conditions with separate urls/views
          and overload them individually here, where necessary, instead of redefining
          the whole if clause.
    """

    model: forum_models.Post = forum_models.Post
    slug_url_kwarg: str = "slug"
    slug_field: str = "slug"
    template_name: str = "django_forum/posts_and_comments/forum_post_detail.html"
    form_class: forum_forms.Post = forum_forms.Post
    comment_form_class: forum_forms.Comment = forum_forms.Comment

    def get(self, request: http.HttpRequest, pk: int, slug: str) -> http.HttpResponse:
        self.object = self.get_object(
            queryset=self.model.objects.select_related("author")
            .select_related("author__profile")
            .select_related("author__profile__avatar")
        )
        context = self.get_context_data()
        context["post"] = self.object
        context["title_errors"] = ""
        context["text_errors"] = ""
        return shortcuts.render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context_data = {}
        context_data["site_url"] = (
            (self.request.scheme or "https") + "://" + conf.settings.SITE_DOMAIN
        )
        context_data["comment_form"] = self.comment_form_class()  # type: ignore
        context_data["subscribed"] = self.object.subscribed_users.filter(
            username=self.request.user.username
        ).count()
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
        try:
            fp = post_model.objects.get(slug=request.POST["slug"])
            if request.POST["data"] == "true":
                fp.subscribed_users.add(request.user)
            else:
                fp.subscribed_users.remove(request.user)
            return http.JsonResponse({}, status=200)
        except post_model.DoesNotExist as e:
            logger.error("There is no post with that slug : {0}".format(e))
            return http.JsonResponse({"error": "no post with that slug"}, status=500)
    else:
        return http.JsonResponse({"error": ""}, status=500)


class PostUpdate(auth.mixins.LoginRequiredMixin, generic.UpdateView):
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
        context_data["post"] = self.model.objects.get(id=self.object.id)
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
        return http.JsonResponse({"url": shortcuts.redirect(post).url}, status=200)


class DeletePost(auth.mixins.LoginRequiredMixin, views.View):
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


class CreateComment(auth.mixins.LoginRequiredMixin, views.generic.CreateView):
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
            s_name=sname,
        )
        return shortcuts.redirect(
            urls.reverse(
                "django_forum:post_view", args=(self.kwargs["pk"], self.kwargs["slug"])
            ),
            permanent=True,
        )

    # def post(self, request: http.HttpRequest, pk: int, slug: str):
    #     post = self.post_model.objects.get(pk=pk, slug=slug)
    #     if not post.moderation_date:
    #         comment_form = self.form_class(data=self.request.POST)
    #         if comment_form.is_valid():
    #             new_comment = comment_form.save(commit=False)
    #             new_comment.author = request.user
    #             new_comment.text = safestring.mark_safe(
    #                 html.unescape(bleach.clean(new_comment.text, strip=False))
    #             )
    #             new_comment.slug = defaultfilters.slugify(
    #                 new_comment.text[:4]
    #                 + "_comment_"
    #                 + str(new_comment.created_at or utils.timezone.now())
    #             )
    #             new_comment.post_fk = post
    #             new_comment.save()
    #             sname: str = "subscribe_timeout" + str(uuid.uuid4())
    #             path: str = "/forum/{}/{}".format(
    #                 self.kwargs["pk"], self.kwargs["slug"]
    #             )
    #             protocol = "https" if self.request.is_secure() else "http"
    #             tasks.schedule(
    #                 "django_forum.tasks.send_subscribed_email",
    #                 self.post_model._meta.app_label
    #                 + "."
    #                 + self.post_model._meta.object_name,
    #                 self.comment_model._meta.app_label
    #                 + "."
    #                 + self.comment_model._meta.object_name,
    #                 name=sname,
    #                 schedule_type="O",
    #                 repeats=-1,
    #                 next_run=utils.timezone.now() + conf.settings.COMMENT_WAIT,
    #                 post_id=post.id,
    #                 comment_id=new_comment.id,
    #                 path=path,
    #                 protocol=protocol,
    #                 s_name=sname,
    #             )
    #             return shortcuts.redirect(new_comment, permanent=True)
    #         else:
    #             site = self.request.get_absolute_url()
    #             comments = self.model.objects.filter(post_fk=post).all()
    #             return shortcuts.render(
    #                 self.request,
    #                 self.template_name,
    #                 {
    #                     "comment_edit": True,
    #                     "post": post,
    #                     "comments": comments,
    #                     "comment_form": comment_form,
    #                     "site_url": (self.request.scheme or "https")
    #                     + "://"
    #                     + site.domain,
    #                 },
    #             )
    #     return shortcuts.redirect(
    #         urls.reverse_lazy(self.a_name + ":post_view", args=[post.id, post.slug]),
    #         permanent=True,
    #     )


class DeleteComment(auth.mixins.LoginRequiredMixin, views.generic.DeleteView):
    model = forum_models.Comment

    def get_success_url(self, *args, **kwwargs):
        return urls.reverse(
            "django_forum:post_view",
            args=(self.object.post_fk.id, self.object.post_fk.slug),
        )


class UpdateComment(auth.mixins.LoginRequiredMixin, views.generic.UpdateView):
    model = forum_models.Comment
    form_class = forum_forms.Comment


class ReportComment(auth.mixins.LoginRequiredMixin, views.View):
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


class ReportPost(auth.mixins.LoginRequiredMixin, views.View):
    http_method_names = ["post"]
    post_model = forum_models.Post
    a_name = "django_forum"

    def post(self, request: http.HttpRequest) -> http.HttpResponseRedirect:
        post = self.post_model.objects.get(
            id=request.POST["post-id"], slug=request.POST["post-slug"]
        )
        if post.author != request.user:
            post.moderation_date = utils.timezone.now()
            post.save(update_fields=["moderation_date"])
            tasks.async_task("django_forum.tasks.send_mod_mail", "Post")
        return shortcuts.redirect(
            urls.reverse_lazy(self.a_name + ":post_view", args=[post.id, post.slug])
        )
