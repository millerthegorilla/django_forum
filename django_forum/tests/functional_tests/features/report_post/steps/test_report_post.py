import pytest

from pytest_bdd import given, scenarios, then, when

from django.core import mail

from django_forum import models as forum_models

scenarios("../report_post.feature")


@when("Post is by different author")
def post_is_by_different_author(test_post, other_user):
    assert test_post.author != other_user


@when("User clicks the moderation link")
def user_clicks_moderation_link(page):
    page.click(".report-post")


@then("Moderation message is visible")
def moderation_message_is_visible(page):
    page.assert_text_visible(
        "This post has been reported and is awaiting moderation. Comments are locked until the post has been validated.",
        "#mod-msg",
    )


@then("Post has a moderation date")
def post_has_moderation_data(post):
    assert post().moderation_date != None


@then("Comments are locked")
def comments_are_locked(page, test_post, post, user_details):
    page.assert_text_visible(
        "Commenting has been locked for this post.", "#comment-locked"
    )
    assert post().commenting_locked == True
