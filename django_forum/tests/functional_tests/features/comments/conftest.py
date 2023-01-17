from pytest_bdd import when, then, given
from django_forum import models as forum_models


@given("A comment exists", target_fixture="test_comment")
def comment_exists(test_post, comment_text):
    return test_post.comments.create(author=test_post.author, text=comment_text)


@when("User clicks the edit comment button")
def user_clicks_the_edit_comment_button(page):
    page.click("#editor-btn")


@then("User clicks the save button")
def user_clicks_the_save_button(db, page):
    page.click("#editor-submit-btn")
