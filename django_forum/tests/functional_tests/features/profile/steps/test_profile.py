"""Profile page feature tests."""
from pytest_bdd import given, scenarios, then, when


scenarios("../profile.feature")


# @given("User is logged in", target_fixture="page")
# def user_is_logged_in(logged_in_page):
#     return logged_in_page


@when("User visits the profile page")
def user_visits_profile_page(page, db):
    page.visit(page.domain + page.pages["profile"])


@then("User can see the display_name input")
def user_can_see_display_nane_input(page):
    assert page.assert_element("#id_display_name")


@then("User can see the username input")
def user_can_see_username_input(page):
    assert page.assert_element("#id_username")


@then("User can see the email input")
def user_can_see_email_input(page):
    assert page.assert_element("#id_email")


@then("User can see the first_name input")
def user_can_see_first_name_input(page):
    assert page.assert_element("#id_first_name")


@then("User can see the last_name input")
def user_can_see_last_name_input(page):
    assert page.assert_element("#id_last_name")


@then("Address details are hidden")
def address_details_are_hidden(page):
    assert not page.is_element_visible("#collapseAddress")


@given("User is not logged in", target_fixture="page")
def user_is_not_logged_in(browser):
    return browser


@then("User is redirected to login page")
def user_is_redirected_to_login_page(page):
    assert "login" in page.get_current_url()


@when("User enters different information")
def user_enter_different_information(page, other_user_details):
    page.type("#id_display_name", other_user_details.display_name)
    page.type("#id_username", other_user_details.username)
    page.type("#id_email", other_user_details.email)
    page.type("#id_first_name", other_user_details.first_name)
    page.type("#id_last_name", other_user_details.last_name)


@when("User clicks submit button")
def user_clicks_submit_button(page, db):
    page.click('button[type="submit"]')


@then("User record is updated")
def user_record_is_updated(django_user_model, other_user_details):
    try:
        user = django_user_model.objects.get(username=other_user_details.username)
        assert user.profile.display_name == other_user_details.display_name
        assert user.email == other_user_details.email
        assert user.first_name == other_user_details.first_name
        assert user.last_name == other_user_details.last_name
    except django_user_model.DoesNotExist:
        raise django_user_model.DoesNotExist("User does not Exist")
