from pytest_bdd import given, scenarios, then, when
from django_forum import models as forum_models

scenarios("../post_text_update.feature")

# Given User is logged in
#         And a post exists
#         When User visits the post view page
#         And User clicks the edit post button
#         Then tinymce is displayed
#         And User changes the post text
#         And User clicks the save button
#         Then the updated post is saved
#         And User is redirected to view post page


@then("tinymce is displayed")
def tinymce_is_displayed(page):
    assert page.driver.execute_script("return tinymce.editors.length") == 1
    assert page.driver.execute_script("return tinymce.editors[0].hidden") == False


@then("User changes the post text")
def user_edits_the_post_text(page, updated_post_text):
    page.switch_to_frame(".tox-edit-area__iframe")
    page.type("#tinymce", updated_post_text)
    page.switch_to_parent_frame()


@then("The updated post text is saved")
def update_post_text_is_saved(updated_post_text):
    post = forum_models.Post.objects.first()
    assert post.text == updated_post_text


@then("User is redirected to view post page")
def user_redirected_to_view_post_page(page, test_post):
    page.assert_title_contains(f"Post")
    page.is_text_visible(test_post.text)
