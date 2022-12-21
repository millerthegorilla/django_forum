from pytest_bdd import when, then
from django_forum import models as forum_models


@when("User clicks the edit post button")
def user_clicks_the_edit_post_button(page):
    page.click("#editor-btn")


@then("User clicks the save button")
def user_clicks_the_save_button(db, page):
    page.click("#editor-submit-btn")
