import pytest

from django_forum import views as forum_views


@pytest.fixture()
def avatar_update():
    return forum_views.UpdateAvatar()


@pytest.fixture()
def forum_profile():
    return forum_views.ForumProfile()
