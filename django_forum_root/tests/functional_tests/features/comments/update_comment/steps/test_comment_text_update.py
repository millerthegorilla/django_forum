from pytest_bdd import given, scenarios, then, when
from django_forum import models as forum_models

scenarios("../comment_text_update.feature")


@when("User clicks the edit comment link")
def user_clicks_edit_comment_link(page):
    page.click("#edit-comment-1")


@then("Textarea is displayed")
def textarea_is_displayed(page):
    page.assert_element_visible("#comment-textarea-1")


@then("User changes the comment text")
def user_changes_the_comment_text(page, updated_comment_text):
    page.type("#comment-textarea-1", updated_comment_text)


@then("User clicks the save link")
def user_clicks_save_link(page):
    page.click("#comment-save-1")


@then("The updated comment text is saved")
def update_comment_text_is_saved(updated_comment_text):
    comment = forum_models.Comment.objects.first()
    assert comment.text == updated_comment_text
