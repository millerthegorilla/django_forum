import pytest
import re
from django_mock_queries.query import MockSet
from django_forum import forms as forum_forms


def test_post_view(rf, mocker, mock_post, mock_user, post_view, db, render_mock):
    mp = mock_post()
    mp.subscribed_users.set = MockSet()
    mocker.patch("django.template.defaulttags.len", return_value=1)
    mocker.patch("django.views.decorators.cache.add_never_cache_headers")
    pk = int(re.findall(r"\d+", re.findall(r"/\d+/", mp.get_absolute_url())[0])[0])
    slug = re.findall(r"/\d+/(.+)", mp.get_absolute_url())[0]
    mp.pk = pk
    mp.slug = slug
    request = rf.get(mp.get_absolute_url)
    request.user = mock_user
    mocker.patch("django_forum.views_forum_post.PostView.get_object", return_value=mp)
    post_view.kwargs = {"pk": pk, "slug": slug}
    post_view.request = request
    response = post_view.get(request, pk=pk, slug=slug)
    assert render_mock.call_args[0][0] == request
    assert (
        render_mock.call_args[0][1]
        == "django_forum/posts_and_comments/forum_post_detail.html"
    )
    assert render_mock.call_args[0][2]["post"] == mp
