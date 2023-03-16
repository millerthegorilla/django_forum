from pytest_bdd import scenarios, then, when

from django_forum import models as forum_models

scenarios("../report_comment.feature")


@when("comment is by different author")
def comment_is_by_different_author(test_comment, other_user):
    assert test_comment.author != other_user


@when("Comment moderation link is visible")
def moderation_link_is_visible(page):
    page.assert_element_visible(".report-comment")


@when("User clicks the moderation link")
def user_clicks_moderation_link(page):
    page.click(".report-comment")


@then("Moderation message is visible")
def moderation_message_is_visible(page):
    page.assert_text_visible(
        "This comment has been reported and is awaiting moderation.",
        "#mod-msg",
    )


@then("comment has a moderation date")
def comment_has_moderation_data():
    comment = forum_models.Comment.objects.first()
    assert comment.moderation_date is not None
