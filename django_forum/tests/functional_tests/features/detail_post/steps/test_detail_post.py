import pytest

from pytest_bdd import given, scenarios, then, when
from django_forum import models as forum_models

scenarios("../detail_post.feature")


@then("The post can be viewed")
def post_can_be_viewed(page, test_post):
    page.assert_text(test_post.text)
