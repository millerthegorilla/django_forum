import pytest
import os
from django.urls import reverse
from django_forum import models as forum_models
from pytest_bdd import given, then, when

CREATE_POST_URL = reverse("django_forum:post_create_view")
# VIEW_POST_URL = forum_models.Post.objects.first().get_absolute_url()
LIST_POST_URL = reverse("django_forum:post_list_view")

PROFILE_URL = reverse("django_forum:profile_update_view")

LINKS_DICT = {
    "create_post": f"a[href='{CREATE_POST_URL}']",
    "list_post": f"a[href='{LIST_POST_URL}']",
    #   "view_post": f"a[href='{VIEW_POST_URL}']",
}

PAGES_DICT = {
    "create_post": CREATE_POST_URL,
    "list_post": LIST_POST_URL,
    "profile": PROFILE_URL,
    #  "view_post": VIEW_POST_URL,
}


@pytest.fixture()
def browser(sb, live_server, settings):
    staging_server = os.environ.get("STAGING_SERVER", False)
    if staging_server:
        sb.visit(staging_server)
    else:
        sb.visit(live_server)
    sb.domain = sb.get_domain_url(sb.get_current_url())
    settings.EMAIL_PAGE_DOMAIN = sb.domain
    sb.pages = PAGES_DICT
    sb.links = LINKS_DICT
    sb.maximize_window()
    return sb


@pytest.fixture()
def create_post_page(browser):
    browser.visit(browser.domain + CREATE_POST_URL)
    return browser


@pytest.fixture()
def profile_page(browser):
    browser.visit(browser.domain + PROFILE_URL)
    return browser


@pytest.fixture()
def post(db, active_user, post_text):
    def posty():
        return forum_models.Post.objects.get_or_create(
            author=active_user, title="Title", text=post_text
        )[0]

    return posty


@given("A post exists", target_fixture="test_post")
def post_exists(post):
    return post()


@pytest.fixture()
def view_post_page(post, browser):
    browser.visit(browser.domain + post.get_absolute_url())
    return browser


@given("User is logged in", target_fixture="page")
def user_is_logged_in(logged_in_page, active_user, user_details):
    return logged_in_page(active_user, user_details.password)


@given("Other user is logged in", target_fixture="page")
def other_user_is_logged_in(logged_in_page, other_user, other_user_details):
    return logged_in_page(other_user, other_user_details.password)


@when("User visits the post view page", target_fixture="page")
@when("Other user visits the post view page", target_fixture="page")
def user_visits_post_view_page(browser, test_post):
    browser.visit(browser.domain + test_post.get_absolute_url())
    return browser


@when("Moderation link is visible")
@then("Moderation link is visible")
def moderation_link_is_visible(page):
    page.assert_element_visible(".report-post")
