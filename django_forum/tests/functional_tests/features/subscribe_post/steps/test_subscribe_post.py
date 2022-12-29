import pytest

from pytest_bdd import given, scenarios, then, when

from django_forum import models as forum_models


scenarios("../subscribe_post.feature")


@then("Subscribe checkbox is not checked")
def subscribe_checkbox_is_not_checked(page):
    assert page.is_checked("#subscribed_cb") == False


@then("User is not subscribed")
def user_is_not_subscribed(active_user, post):
    with pytest.raises(forum_models.Post.DoesNotExist):
        active_user.subscribed_posts.get(title=post.title)
