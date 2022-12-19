from pytest_bdd import given, scenarios, then, when

scenarios("../post_list.feature")


# for some reason, if I don't instantiate the
# browser before the message, it isn't added
@given("A post exists", target_fixture="post")
def post_exists(browser, test_post):
    test_post.save()
    return test_post


@when("User visits the post list page", target_fixture="page")
def user_visits_posts_page(db, browser):
    browser.visit(browser.domain + browser.pages["list_post"])
    return browser


@then("The post is listed")
def post_is_listed(message, page):
    page.assert_element(f"a[href='/{post.id}/{post.slug}/']")
