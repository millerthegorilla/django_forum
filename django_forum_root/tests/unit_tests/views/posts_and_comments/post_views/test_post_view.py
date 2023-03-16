import re

import pytest
from django_mock_queries.query import MockSet

from django_forum import forms as forum_forms


def test_post_view(rf, mocker, mock_post, mock_user, post_view, db, render_mock):
    m_p = mock_post()
    m_p.subscribed_users.set = MockSet()
    mocker.patch("django.template.defaulttags.len", return_value=1)
    mocker.patch("django.views.decorators.cache.add_never_cache_headers")
    request = rf.get(m_p.get_absolute_url)
    request.user = mock_user()
    mocker.patch("django_forum.views_forum_post.PostView.get_object", return_value=m_p)
    post_view.kwargs = {"pk": m_p.pk, "slug": m_p.slug}
    post_view.request = request
    post_view.get(request, pk=m_p.pk, slug=m_p.slug)
    assert render_mock.call_args[0][0] == request
    assert (
        render_mock.call_args[0][1]
        == "django_forum/posts_and_comments/forum_post_detail.html"
    )
    assert render_mock.call_args[0][2]["post"] == m_p
