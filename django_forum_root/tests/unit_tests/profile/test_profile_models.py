import pytest

from django.contrib.auth import get_user_model
from django.db import IntegrityError

from django_forum import models as forum_models

User = get_user_model()


def test_create_a_user_creates_a_profile(user, user_details, db):
    user = user(user_details)
    profile = forum_models.ForumProfile.objects.last()
    assert user.profile == profile


def test_create_a_profile_with_no_user_raises_integrity_error(db):
    with pytest.raises(IntegrityError):
        forum_models.ForumProfile.objects.create()
