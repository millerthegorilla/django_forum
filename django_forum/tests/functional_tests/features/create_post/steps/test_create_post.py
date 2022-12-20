from pytest_bdd import given, scenarios, then, when

from django_forum import models as forum_models

scenarios("../create_post.feature")


@when("User is on the create post page", target_fixture="page")
def user_is_on_create_post_page(create_post_page):
    return create_post_page


@when("User enters some text")
def user_enters_some_text(page, post_text):
    page.type("#id_title", "post title")
    page.switch_to_frame("id_text_ifr")
    page.type("#tinymce", post_text())
    page.switch_to_parent_frame()


@when("User clicks the save button")
def user_clicks_save_button(page, db):
    page.click('input[type="submit"]')


@then("Post is stored in database")
def post_is_stored_in_database(db, post_text):
    assert forum_models.Post.objects.first().text == post_text()


@then("User is taken to post detail page")
def user_is_taken_to_post_detail_page(db, page):
    post_text = forum_models.Post.objects.first().text
    assert "Post" in page.get_page_title()
    page.assert_text(post_text, selector="#textarea")
