from pytest_bdd import given, scenarios, then, when

scenarios("../post_list.feature")


@given("A post exists", target_fixture="test_post")
def post_exists(browser, post):
    return post


@when("User visits the post list page", target_fixture="page")
def user_visits_posts_page(db, browser):
    browser.visit(browser.domain + browser.pages["list_post"])
    return browser


@then("The post is listed")
def post_is_listed(test_post, page):
    page.assert_element(f"a[href='/post/{test_post.id}/{test_post.slug}/']")
