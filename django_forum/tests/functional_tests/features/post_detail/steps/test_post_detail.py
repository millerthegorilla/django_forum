import pytest

from pytest_bdd import given, scenarios, then, when
from django_forum import models as forum_models

scenarios("../post_detail.feature")


@given("A page", target_fixture="page")
def a_page(browser):
    return browser


@when("User visits the correct url")
def user_visits_the_correct_url(db, page, test_post):
    page.visit(page.domain + f"/{test_post.id}/{test_post.slug}")
    return page


@then("The message can be viewed")
def the_message_can_be_viewed(page, test_post):
    page.assert_text(test_post.text)
