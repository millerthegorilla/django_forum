import pytest
from django import http
from django.contrib.auth import get_user_model

from django_forum import forms as forum_forms
from django_forum import views_forum_post as forum_post_views

User = get_user_model()


@pytest.fixture()
def postcreate_view():
    return forum_post_views.PostCreate()


def test_post_create_form_valid_with_subscribe(
    mocker, rf, active_user, mock_post, postcreate_view
):
    mocker.patch("django.contrib.auth.models.User")
    postcreate_view.request = rf.post("/create_post/")
    postcreate_view.request.user = active_user
    postcreate_view.request.POST = {"subscribe": "True"}
    postcreate_view.get_success_url = mocker.MagicMock()
    postcreate_view.get_success_url.return_value = "/post/"
    mocker.patch("django_forum.forms.Post")
    mocker.patch("django_forum.models.Post.subscribed_users")
    mocker.patch("django_forum.models.Post.save")
    # mocker_post.get_absolute_url.return_value =
    form = forum_forms.Post()
    form.save = mocker.MagicMock()
    mp = mock_post()
    form.save.return_value = mp
    response = postcreate_view.form_valid(form)
    mp.subscribed_users.add.assert_called_once()
    assert mp.save.call_count == 2
    # mp.save.assert_called_once()
    assert type(response) == http.response.HttpResponseRedirect
    assert response.status_code == 302


def test_post_create_form_valid_wout_subscribe(
    mocker, rf, active_user, mock_post, postcreate_view
):
    mocker.patch("django.contrib.auth.models.User")
    postcreate_view.request = rf.post("/create_post/")
    postcreate_view.request.user = active_user
    postcreate_view.request.POST = {}
    postcreate_view.get_success_url = mocker.MagicMock()
    postcreate_view.get_success_url.return_value = "/post/"
    mocker.patch("django_forum.forms.Post")
    mocker.patch("django_forum.models.Post.subscribed_users")
    mocker.patch("django_forum.models.Post.save")
    form = forum_forms.Post()
    form.save = mocker.MagicMock()
    mp = mock_post()
    form.save.return_value = mp
    response = postcreate_view.form_valid(form)
    mp.subscribed_users.add.assert_not_called()
    assert mp.save.call_count == 2
    # mp.save.assert_called_once()
    assert type(response) == http.response.HttpResponseRedirect
    assert response.status_code == 302


def test_post_create_view_get_success_url(mocker, postcreate_view, mock_post):
    mp = mock_post()
    mp.slug = "1000000Bananas"
    response = postcreate_view.get_success_url(mp)
    assert response == "/post/1/1000000Bananas/"
