from pytest_bdd import given, scenarios, then, when

from django_forum import models as forum_models

scenarios("../create_comment.feature")


@when("User is on the create comment page", target_fixture="page")
def user_is_on_create_comment_page(create_comment_page):
    return create_comment_page


@when("User enters some text in the comment box")
def user_enters_some_text_in_comment_box(page, comment_text):
    page.type("#comment-text", comment_text)


@when("User clicks the save button")
def user_clicks_save_button(page, db):
    page.click("#submit-comment")


@then("Comment is stored in database")
def comment_is_stored_in_database(db, comment_text):
    assert forum_models.Comment.objects.first().text == comment_text


@then("User is taken to comment anchor of post detail page")
def user_is_taken_to_comment_anchor_post_detail_page(db, page):
    comment = forum_models.Comment.objects.first()
    page.assert_text(comment.text, selector="#comment-text-1")
