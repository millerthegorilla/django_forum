import django
import pytest
from django.db.models import base as django_db_base
from faker import Faker
from safe_imagefield.models import SafeImageField

fake = Faker()


@pytest.fixture()
def render_mock(mocker):
    return mocker.patch("django_forum.views_forum_post.shortcuts.render")


@pytest.fixture()
def mock_user(mocker):
    def m_u():
        mock_profile = mocker.patch("django_forum.models.ForumProfile")
        mock_avatar = mocker.patch("django_forum.models.Avatar")
        mock_profile.return_value.avatar = mock_avatar
        mock_image_file = mocker.Mock(spec=SafeImageField)
        mock_user = mocker.create_autospec(
            django.contrib.auth.models.User, instance=True
        )
        mock_user._state = django_db_base.ModelState()
        mock_user.username = fake.user_name()
        type(mock_avatar).image_file = mocker.PropertyMock(return_value=mock_image_file)
        type(mock_profile).avatar = mocker.PropertyMock(return_value=mock_avatar)
        type(mock_profile).display_name = mocker.PropertyMock(
            return_value=fake.user_name()
        )
        type(mock_user).profile = mocker.PropertyMock(return_value=mock_profile)
        return mock_user

    return m_u
