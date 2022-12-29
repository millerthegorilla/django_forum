from pytest_bdd import given, scenarios, then, when
from django_forum import models as forum_models

scenarios("../post_title_update.feature")


UPDATED_TITLE_TEXT = "the first post title edited"


@then("The title is editable")
def title_is_editable(page):
    page.get_element(".post-edit-div").is_displayed()


@then("User changes the post title")
def user_changes_the_post_title(page):
    page.type("#title-input", UPDATED_TITLE_TEXT)


@then("The updated post title is saved")
def update_post_title_is_saved():
    post = forum_models.Post.objects.first()
    assert post.title == UPDATED_TITLE_TEXT


@then("User is redirected to view post page")
def user_redirected_to_view_post_page(page, test_post):
    page.assert_title_contains(f"Post")
    page.assert_text("the first post title edited")
