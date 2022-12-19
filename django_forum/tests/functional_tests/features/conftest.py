import pytest
import os
from django.urls import reverse
from django_forum import models as forum_models

POST_TEXT = "Ipsum Lorum Dolum Est"

CREATE_POST_URL = reverse("django_forum:post_create_view")
LIST_POST_URL = reverse("django_forum:post_list_view")

LINKS_DICT = {
    "create_post": f"a[href='{CREATE_POST_URL}']",
    "list_message": f"a[href='{LIST_POST_URL}']",
}

PAGES_DICT = {
    "create_post": CREATE_POST_URL,
    "list_post": LIST_POST_URL,
}


@pytest.fixture()
def post_text():
    return lambda: POST_TEXT


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
    return sb


@pytest.fixture()
def create_post_page(browser):
    browser.visit(browser.domain + CREATE_POST_URL)
    return browser
