from typing import Any, Callable
from urllib.parse import urlparse

import pytest
from django_mock_queries.query import MockSet

from django_forum import forms as forum_forms
from django_forum import models as forum_models
from django_forum import views_forum_post as forum_post_views


def test_form_valid(
    mocker,
    comment_create: forum_post_views.CreateComment,
    mock_post: Callable[[], Any],
    mock_comment: Callable[[], Any],
    rf,
):  # pylint: disable=C0116
    tasks = forum_post_views.tasks = mocker.MagicMock()
    m_p = mock_post()
    m_c = mock_comment()
    m_c.save = mocker.MagicMock()
    post_model: forum_models.Post = mocker.patch.object(comment_create, "post_model")
    comment_create.request = rf.post(f"/delete_post/{m_p.pk}/{m_p.slug}/")
    comment_create.request.user = m_p.author
    post_model.objects.get.return_value = m_p
    comment_create.kwargs = {"pk": m_p.pk, "slug": m_p.slug}
    form = mocker.patch("django_forum.forms.Comment", autospec=True)
    form.save.return_value = m_c
    response = comment_create.form_valid(form)
    assert response.status_code == 301
    assert response.url == "/post" + str(urlparse(m_p.get_absolute_url()).path) + "/"
    assert (
        tasks.schedule.call_count
        == m_c.save.call_count
        == form.save.call_count
        == 1  # noqa: E501
    )


def test_form_invalid(
    mocker,
    comment_create: forum_post_views.CreateComment,
    mock_post,
    render_mock: Any,
    rf,
):
    m_p = mock_post()
    request = rf.post(f"/delete_post/{m_p.pk}/{m_p.slug}/")
    request.user = m_p.author
    comment_create.request = request
    post_form = mocker.MagicMock()
    comments = mocker.MagicMock()
    c_c = mocker.patch.object(comment_create, "get_context_data")
    c_c.return_value = {
        "form": post_form,
        "post": m_p,
        "comments": comments,
    }
    comment_form = mocker.patch("django_forum.forms.Comment", autospec=True)
    comment_create.form_invalid(comment_form)
    render_mock.assert_called_once_with(
        request,
        comment_create.template_name,
        {
            "form": post_form,
            "post": m_p,
            "comments": comments,
            "comment_form": comment_form,
        },
    )
