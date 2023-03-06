import pytest
from django_forum import views as forum_views
from django_forum import models as forum_models


@pytest.fixture()
def profile_get_request(rf, active_user):
    request = rf.get("/profile")
    request.user = active_user
    return request


@pytest.fixture()
def profile_post_request(rf, active_user, mocker):
    def post_request(first_name=None, email=None):
        data = {
            "display_name": active_user.profile.display_name,
            "username": active_user.username,
            "email": active_user.email if email is None else email,
            "first_name": active_user.first_name if first_name is None else first_name,
            "last_name": active_user.last_name,
        }
        request = rf.post("/profile", data)
        request.user = active_user
        return request

    return post_request


@pytest.fixture()
def profile_update(profile_get_request):
    profile_update = forum_views.ForumProfile()
    profile_update.request = profile_get_request
    return profile_update


@pytest.fixture()
def profile_get_response(profile_update, profile_get_request):
    return profile_update.get(profile_get_request)
