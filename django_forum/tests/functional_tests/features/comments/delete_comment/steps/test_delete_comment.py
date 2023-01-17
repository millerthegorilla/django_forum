import pytest

from pytest_bdd import given, scenarios, then, when
from django_forum import models as forum_models

scenarios("../delete_comment.feature")


@when("User clicks the delete comment link")
def user_clicks_delete_comment_button(page):
    page.click("#delete-comment-1")


@then("Comment delete modal is shown")
def comment_delete_modal_is_shown(page):
    page.assert_element_visible("#comment-modal")


@then("User clicks the confirm button")
def user_clicks_confirm_button(page):
    page.click("/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div/div[3]/form/button")


@then("Comment is deleted")
def comment_is_deleted(comment_text):
    with pytest.raises(forum_models.Comment.DoesNotExist):
        forum_models.Comment.objects.get(text=comment_text)


@then("User is taken to post view")
def user_is_taken_to_post_view(page):
    assert "/post/" in page.get_current_url()
