import pytest

from pytest_bdd import given, scenarios, then, when

from django.contrib.auth import get_user_model

from django_forum import models as forum_models

User = get_user_model()


@pytest.fixture()
def subscribed_user(active_user, test_post):
    test_post.subscribed_users.add(active_user)
    return active_user


@when("User clicks subscribe checkbox")
def user_clicks_subscribe_checkbox(page):
    page.click("#subscribed_cb")
    page.wait(0.2)


@given("User is subscribed")
@then("User is subscribed")
@when("User is subscribed")
def user_is_subscribed(db, test_post, subscribed_user):
    try:
        test_post.subscribed_users.get(username=subscribed_user.username)
    except User.DoesNotExist as e:
        assert False, f"User {subscribed_user.username} is not subscribed"


# @when("Browser is refreshed")
# def browser_is_refreshed(page):
#     page.open(page.get_current_url())
#     page.wait_for_ready_state_complete()
#     return page
# page.refresh_page() - doesn't work in headless
