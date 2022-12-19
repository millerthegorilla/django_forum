from pytest_bdd import given, scenarios, then, when
from django_forum import models as forum_models

scenarios("../post_update.feature")


@given("A post exists", target_fixture="post")
def post_exists(browser, test_post):
    return test_post


@when("User visits the update post page", target_fixture="page")
def user_visits_update_post_page(browser, post):
    browser.visit(browser.domain + f"/update_post/{post.id}/{post.slug}/")
    return browser


@when("User edits the message text")
def user_edits_the_message_text(page, message):
    page.type("#id_text", message.text + " I am updated.")


@when("User clicks the save button")
def user_clicks_the_save_button(db, page):
    page.click("input[type='submit']")


@then("The updated message is saved")
def update_message_is_saved():
    message = message_models.Message.objects.first()
    assert "I am updated." in message.text


@then("User is redirected to view message page")
def user_redirected_to_view_message_page(page, message):
    page.is_text_visible(message.text)
    page.assert_title_contains(f"Message {message.id}")
