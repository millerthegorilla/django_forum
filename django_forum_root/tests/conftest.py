import random
import pytest
from faker import Faker

from django.urls import reverse
from django.template import defaultfilters


POST_TEXT = "Ipsum Lorum Dolum Est"
UPDATED_POST_TEXT = "Pissum Lawum Dole Est"
COMMENT_TEXT = "Commenting is fun for trolls"
UPDATED_COMMENT_TEXT = "Commenting is fun for trolls and james"


@pytest.fixture()
def post_text():
    return POST_TEXT


@pytest.fixture()
def updated_post_text():
    return UPDATED_POST_TEXT


@pytest.fixture()
def comment_text():
    return COMMENT_TEXT


@pytest.fixture()
def updated_comment_text():
    return UPDATED_COMMENT_TEXT


class UserDetails:
    def __init__(self):
        fake = Faker("en_GB")
        fake.random.seed(random.randint(0, 999))
        self.first_name = fake.first_name()
        self.last_name = fake.last_name()
        self.display_name = self.first_name + " " + self.last_name
        self.address1 = (
            str(random.randint(1, 50))
            + " "
            + fake.street_name()
            + " "
            + fake.street_suffix()
        )
        self.address2 = fake.street_name()
        self.city = fake.city()
        self.country = fake.country()
        self.postcode = fake.postcode().replace(" ", "")
        self.domain = fake.domain_name()
        self.username = self.first_name + str(random.randint(101, 999))
        self.password = fake.password(14)
        self.email = self.first_name + "_" + self.last_name + "@" + self.domain


@pytest.fixture()
def user_details():
    return UserDetails()


@pytest.fixture()
def other_user_details():
    return UserDetails()


@pytest.fixture()
def user(
    transactional_db, django_user_model
):  # transactional_db because using live_server
    def create_user(details):
        user = django_user_model.objects.get_or_create(
            username=details.username,
            password=details.password,  # https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests  # noqa: E501
            first_name=details.first_name,
            last_name=details.last_name,
            email=details.email,
        )
        theuser = user[0]
        if user[1] == True:
            theuser.set_password(details.password)
            theuser.is_active = False
            theuser.save()
            theuser.profile.display_name = defaultfilters.slugify(
                details.first_name + " " + details.last_name
            )
            theuser.profile.save(update_fields=["display_name"])
        return theuser

    return create_user


@pytest.fixture()
def active_user(user, user_details):
    a_user = user(user_details)
    a_user.is_active = True
    a_user.is_superuser = True
    a_user.save()
    return a_user


@pytest.fixture()
def other_user(user, other_user_details):
    o_user = user(other_user_details)
    o_user.is_active = True
    o_user.save()
    return o_user


@pytest.fixture()
def logged_in_page(browser, db):
    def page(user, password):
        browser.visit(browser.domain + reverse("django_users:login"))
        browser.type("#id_username", user.username)
        browser.type("#id_password", password)
        browser.click('button[type="submit"]')
        return browser

    return page


@pytest.fixture()
def auto_login_user(db, client, active_user):
    def make_auto_login(user=None):
        if user is None:
            user = active_user
        client.login(username=user.username, password=user.password)
        return client, user

    return make_auto_login


def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
):
    print(f"step failed {step}")
