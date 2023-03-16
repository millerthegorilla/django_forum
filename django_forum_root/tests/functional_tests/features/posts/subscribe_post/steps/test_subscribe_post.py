import pytest
from django_q import models as q_models
from pytest_bdd import scenarios, then, when

from django_forum import models as forum_models

scenarios("../subscribe_post.feature")


@then("Subscribe checkbox is checked")
@when("Subscribe checkbox is checked")
def subscribe_checkbox_is_checked(page):
    assert page.is_checked("#subscribed_cb")


@then("Browser is refreshed and subscribe checkbox is checked")
def refresh_browser_and_subscribe_checkbox_is_checked(page):
    page.refresh()
    assert page.is_checked("#subscribed_cb")


@then("Browser is refreshed and subscribe checkbox is not checked")
def refresh_browser_and_subscribe_checkbox_is_not_checked(page):
    page.refresh()
    assert page.find_element("#subscribed_cb").is_selected() == False


@then("User is not subscribed")
def user_is_not_subscribed(active_user, test_post, page):
    page.sleep(0.02)
    with pytest.raises(forum_models.Post.DoesNotExist):
        active_user.subscribed_posts.get(title=test_post.title)


@when("Other user creates a comment")
def other_user_creates_comment(page, comment_text):
    page.type("#comment-text", comment_text)
    page.click("#submit-comment")


@then("A task is scheduled")
def task_is_scheduled():
    assert "django_forum.tasks.send_subscribed_email" == str(
        q_models.Schedule.objects.first()
    )
