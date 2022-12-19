import random

import pytest
from django.urls import reverse
from faker import Faker


class UserDetails:
    def __init__(self):
        fake = Faker()
        fake.random.seed(random.randint(0, 999))
        self.first_name = fake.first_name()
        self.last_name = fake.last_name()
        self.domain = fake.domain_name()
        self.username = self.first_name + str(random.randint(101, 999))
        self.password = fake.password(14)
        self.email = self.first_name + "_" + self.last_name + "@" + self.domain


@pytest.fixture()
def user_details():
    return UserDetails()


@pytest.fixture()
def different_user_details():
    return UserDetails()


@pytest.fixture()
def user(
    transactional_db, user_details, django_user_model
):  # transactional_db because using live_server
    user = django_user_model.objects.create(
        username=user_details.username,
        password=user_details.password,  # https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests  # noqa: E501
        first_name=user_details.first_name,
        last_name=user_details.last_name,
        email=user_details.email,
    )
    user.set_password(user_details.password)
    user.is_active = False
    user.save()
    yield user
    user.delete()


@pytest.fixture()
def active_user(user):
    user.is_active = True
    user.save()
    return user


@pytest.fixture()
def logged_in_page(browser, active_user, db, user_details):
    browser.visit(browser.domain + reverse("django_users:login"))
    browser.type("#id_username", active_user.username)
    browser.type("#id_password", user_details.password)
    browser.click('button[type="submit"]')
    return browser


@pytest.fixture()
def auto_login_user(db, client, active_user):
    def make_auto_login(user=None):
        if user is None:
            user = active_user
        client.login(username=user.username, password=user.password)
        return client, user

    return make_auto_login
