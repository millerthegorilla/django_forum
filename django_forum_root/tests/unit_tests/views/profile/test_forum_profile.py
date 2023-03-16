from dataclasses import dataclass

import django
import pytest


@pytest.fixture()
def setup_test(rf, mock_user, mocker, forum_profile):
    m_u = mock_user()
    request = rf.post("/profile/")
    request.user = m_u
    form = mocker.patch.object(forum_profile, "form_class")
    user_form = mocker.patch.object(forum_profile, "user_form_class")
    model = mocker.patch.object(forum_profile, "model")
    model.objects.get.return_value.avatar = mocker.MagicMock()
    return (
        m_u,
        request,
        form,
        user_form,
        forum_profile,
    )


def test_forum_profile_post_without_errors(setup_test, mocker):
    m_u, request, form, user_form, forum_profile = setup_test
    form.return_value.errors = user_form.return_value.errors = None
    response = forum_profile.post(request)
    assert type(response) == django.http.response.HttpResponseRedirect
    assert response.status_code == 302
    assert response.url == forum_profile.success_url


def test_forum_profile_with_username_errors(render_mock, setup_test, mocker):
    m_u, request, form, user_form, forum_profile = setup_test
    user_form.return_value.errors.__getitem__.return_value = (
        django.forms.utils.ErrorList(["contains illegal characters"])
    )
    mocker.patch("django_forum.views.len", return_value=1)
    response = forum_profile.post(request)
    pass
