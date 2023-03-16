import pytest


def test_post_delete_post(mocker, post_delete, mock_post, rf, redirect_mock, mock_user):
    m_u = mock_user()
    mp = mock_post()
    mp.delete = mocker.MagicMock()
    type(mp).author = mocker.PropertyMock(return_value=m_u)
    Post = mocker.patch.object(post_delete, "model")
    Post.objects.get.return_value = mp
    request = rf.post(f"delete_post/{mp.pk}/{mp.slug}/")
    request.user = m_u
    post_delete.post(request, mp.pk, mp.slug)
    mp.delete.assert_called_once()
    redirect_mock.assert_called_once_with("/posts/")
