import pytest

from pytest_bdd import given, scenarios, then, when
from django_forum import models as forum_models

scenarios("../delete_post.feature")


@when("User clicks the delete button")
def user_clicks_delete_post_button(page):
    page.click("#delete-btn")


@then("Post Delete modal is shown")
def post_delete_modal_is_shown(page):
    page.assert_element_visible("#confirmDeleteModal")


@then("User clicks the confirm button")
def user_clicks_confirm_button(page):
    page.click("/html/body/div[1]/div[2]/div/div[1]/div[4]/div/div/div[3]/form/button")


@then("Post is deleted")
def post_is_deleted(post_text):
    with pytest.raises(forum_models.Post.DoesNotExist):
        forum_models.Post.objects.get(text=post_text)


@then("User is taken to post list page")
def user_is_taken_to_post_list_page(page):
    assert "Forum Posts" in page.get_page_title()
    assert "There are currently no posts in the forum" in page.get_page_source()
