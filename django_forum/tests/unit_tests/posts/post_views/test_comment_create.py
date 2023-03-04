from typing import Any, Callable, Literal
import pytest
import sys
from django_mock_queries.query import MockSet
from urllib.parse import urlparse
from django_forum.models import Comment, Post
from django_forum import views_forum_post as forum_post_views


def test_form_valid(
    mocker,
    comment_create: forum_post_views.CreateComment,
    mock_post: Callable[[], Any],
    mock_comment: Callable[[], Any],
    rf,
):  # pylint: disable=C0116
    tasks = forum_post_views.tasks = mocker.MagicMock()
    mp = mock_post()
    mc = mock_comment()
    mc.save = mocker.MagicMock()
    post_model: Post = mocker.patch.object(comment_create, "post_model")
    comment_create.request = rf.post(f"/delete_post/{mp.pk}/{mp.slug}/")
    comment_create.request.user = mp.author
    post_model.objects.get.return_value = mp
    comment_create.kwargs = {"pk": mp.pk, "slug": mp.slug}
    form = mocker.patch("django_forum.forms.Comment", autospec=True)
    form.save.return_value = mc
    response = comment_create.form_valid(form)
    assert response.status_code == 301
    assert response.url == "/post" + urlparse(mp.get_absolute_url()).path + "/"
    assert (
        tasks.schedule.call_count
        == mc.save.call_count
        == form.save.call_count
        == 1  # noqa: E501
    )


@pytest.mark.locutus
def test_form_invalid(mocker, comment_create: forum_post_views.CreateComment):
    form = mocker.patch("django_forum.forms.Comment", autospec=True)
    post_model = mocker.patch.object(comment_create, "post_model")
    
