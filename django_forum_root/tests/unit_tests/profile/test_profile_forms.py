import pytest


from django_forum import forms as forum_forms


def test_user_profile_validation_email(db, user_details):
    bob = user_details.__dict__
    bob["email"] = "bob@bo"
    form = forum_forms.ForumUserProfile(bob)
    assert len(form.errors) == 1
    assert form.errors["email"][0] == "Enter a valid email address."


def test_user_profile_rejects_existing_user(db, active_user):
    bob = active_user.__dict__
    bob["display_name"] = active_user.profile.display_name
    form = forum_forms.ForumUserProfile(bob)
    assert len(form.errors) == 1
    assert form.errors["username"][0] == "A user with that username already exists."


def test_profile_excludes_profile_user():
    form = forum_forms.ForumProfile()
    with pytest.raises(KeyError):
        form["profile_user"]
