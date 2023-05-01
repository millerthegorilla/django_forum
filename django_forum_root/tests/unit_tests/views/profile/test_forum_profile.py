from dataclasses import dataclass

import django
import pytest
from django.forms import utils


@pytest.fixture()
def setup_test(rf, mock_user, mocker, forum_profile):
    m_u = mock_user()
    request = rf.post("/profile/")
    request.user = m_u
    form = mocker.patch.object(forum_profile, "form_class")
    user_form = mocker.patch.object(forum_profile, "user_form_class")
    model = mocker.patch.object(forum_profile, "model")
    avatar = mocker.MagicMock()
    model.objects.get.return_value.avatar = avatar
    return (
        m_u,
        request,
        form,
        user_form,
        forum_profile,
        model,
        avatar,
    )


def test_forum_profile_post_without_errors(setup_test, mocker):
    m_u, request, form, user_form, forum_profile, model = setup_test
    form.return_value.errors = user_form.return_value.errors = None
    response = forum_profile.post(request)
    assert type(response) == django.http.response.HttpResponseRedirect
    assert response.status_code == 302
    assert response.url == forum_profile.success_url


def test_forum_profile_with_username_errors(render_mock, setup_test, mocker):
    m_u, request, form, user_form, forum_profile, model, avatar = setup_test
    user_form.return_value.errors = utils.ErrorDict(
        {"username": utils.ErrorList(["contains illegal characters"])}
    )
    form.return_value.errors = utils.ErrorDict()
    form.return_value.fields = {}
    response = forum_profile.post(request)
    pass
