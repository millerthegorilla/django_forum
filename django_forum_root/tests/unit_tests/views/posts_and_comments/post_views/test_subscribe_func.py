import pytest
from django_mock_queries.query import MockSet

from django_forum import models as forum_models
from django_forum.views_forum_post import subscribe


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
    m_u = mock_user()
    mock_post_set = mocker.patch("django_forum.models.Post.objects")
    mock_user_set = MockSet()
    mock_user_set.add(m_u)
    mock_user_set.remove = mocker.MagicMock()
    m_p = mock_post()
    s_u = mocker.PropertyMock(return_value=mock_user_set)
    type(m_p).subscribed_users = s_u
    mock_post_set.prefetch_related.return_value.get.return_value = m_p
    request = rf.post(
        "/subscribe/",
        {"slug": m_p.slug, "data": "false"},
        **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
    )
    request.user = m_u
    json_response = subscribe(request)
    m_p.subscribed_users.remove.assert_called_once_with(m_u)
    assert json_response.status_code == 200


def test_subscribe_func_remove_no_user(rf, mock_post, mock_user, mocker):
    mock_post_set = mocker.patch("django_forum.models.Post.objects")
    m_p = mock_post()
    mock_post_set.prefetch_related.return_value.get = mocker.MagicMock(
        side_effect=m_p.DoesNotExist
    )
    request = rf.post(
        "/subscribe/",
        {"slug": m_p.slug, "data": "false"},
        **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
    )
    request.user = mock_user()
    with pytest.raises(m_p.DoesNotExist):
        subscribe(request)
