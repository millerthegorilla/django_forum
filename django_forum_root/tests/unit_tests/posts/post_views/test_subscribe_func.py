import pytest
from django_mock_queries.query import MockSet

from django_forum.views_forum_post import subscribe
from django_forum import models as forum_models


def test_subscribe_func_add(rf, mock_post, mock_user, mocker):
    mock_post_set = mocker.patch("django_forum.models.Post.objects")
    mock_user_set = MockSet()
    mock_user_set.add = mocker.MagicMock()
    mp = mock_post()
    su = mocker.PropertyMock(return_value=mock_user_set)
    type(mp).subscribed_users = su
    su.add = mocker.MagicMock()
    mock_post_set.prefetch_related.return_value.get.return_value = mp
    request = rf.post(
        "/subscribe/",
        {"slug": mp.slug, "data": "true"},
        **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
    )
    request.user = mock_user
    json_response = subscribe(request)
    mp.subscribed_users.add.assert_called_once_with(mock_user)
    assert json_response.status_code == 200


def test_subscribe_func_remove_subscribed_user(rf, mock_post, mock_user, mocker):
    mock_post_set = mocker.patch("django_forum.models.Post.objects")
    mock_user_set = MockSet()
    mock_user_set.add(mock_user)
    mock_user_set.remove = mocker.MagicMock()
    mp = mock_post()
    su = mocker.PropertyMock(return_value=mock_user_set)
    type(mp).subscribed_users = su
    mock_post_set.prefetch_related.return_value.get.return_value = mp
    request = rf.post(
        "/subscribe/",
        {"slug": mp.slug, "data": "false"},
        **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
    )
    request.user = mock_user
    json_response = subscribe(request)
    mp.subscribed_users.remove.assert_called_once_with(mock_user)
    assert json_response.status_code == 200


def test_subscribe_func_remove_no_user(rf, mock_post, mock_user, mocker):
    mock_post_set = mocker.patch("django_forum.models.Post.objects")
    mp = mock_post()
    mock_post_set.prefetch_related.return_value.get = mocker.MagicMock(
        side_effect=mp.DoesNotExist
    )
    request = rf.post(
        "/subscribe/",
        {"slug": mp.slug, "data": "false"},
        **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
    )
    request.user = mock_user
    with pytest.raises(mp.DoesNotExist):
        json_response = subscribe(request)
