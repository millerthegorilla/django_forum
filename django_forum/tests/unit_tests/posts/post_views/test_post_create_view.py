import pytest
import uuid
from django import http
from django.contrib.auth import get_user_model
from django_forum import models as forum_models
from django_forum import views as forum_views
from django_forum import views_forum_post as forum_post_views
from django_forum import forms as forum_forms


User = get_user_model()


@pytest.fixture()
def postcreate_view():
    return forum_post_views.PostCreate()


def test_post_create_get_context_data_no_form(mocker):
    mocker.patch(
        "django_forum.views_forum_post.PostCreate.form_class",
        new_callable=mocker.PropertyMock,
    )
    response = pc_view.get_context_data()
    assert type(response) == dict
    forum_post_views.PostCreate.form_class.assert_called_once()


def test_post_create_get_context_data_with_form_and_error(mocker):
    mocker.patch("django_forum.forms.Post")
    # mocker.patch("django_forum.forms.Post.errors")
    form = forum_forms.Post()
    form.errors.keys = mocker.MagicMock()
    form.errors.keys.return_value = ["text"]
    response = pc_view.get_context_data(form)


def test_post_create_form_valid_with_subscribe(
    mocker, rf, active_user, mock_post, postcreate_view
):
    user = mocker.patch("django.contrib.auth.models.User")
    postcreate_view.request = rf.post("/create_post/")
    postcreate_view.request.user = active_user
    postcreate_view.request.POST = {"subscribe": "True"}
    postcreate_view.get_success_url = mocker.MagicMock()
    postcreate_view.get_success_url.return_value = "/post/"
    mocker.patch("django_forum.forms.Post")
    mocker.patch("django_forum.models.Post.subscribed_users")
    # mocker_post.get_absolute_url.return_value =
    form = forum_forms.Post()
    form.save = mocker.MagicMock()
    form.save.return_value = mock_post
    response = postcreate_view.form_valid(form)
    mock_post.subscribed_users.add.assert_called_once()
    mock_post.save.assert_called_once()
    assert type(response) == http.response.HttpResponseRedirect
    assert response.status_code == 302


def test_post_create_form_valid_wout_subscribe(
    mocker, rf, active_user, mock_post, postcreate_view
):
    user = mocker.patch("django.contrib.auth.models.User")
    postcreate_view.request = rf.post("/create_post/")
    postcreate_view.request.user = active_user
    postcreate_view.request.POST = {}
    postcreate_view.get_success_url = mocker.MagicMock()
    postcreate_view.get_success_url.return_value = "/post/"
    mocker.patch("django_forum.forms.Post")
    mocker.patch("django_forum.models.Post.subscribed_users")
    form = forum_forms.Post()
    form.save = mocker.MagicMock()
    form.save.return_value = mock_post
    response = postcreate_view.form_valid(form)
    mock_post.subscribed_users.add.assert_not_called()
    mock_post.save.assert_called_once()
    assert type(response) == http.response.HttpResponseRedirect
    assert response.status_code == 302


def test_post_create_view_get_success_url(mocker, postcreate_view, mock_post):
    mock_post.id = 1
    mock_post.slug = "1000000Bananas"
    response = postcreate_view.get_success_url(mock_post)
    assert response == "/post/1/1000000Bananas/"
