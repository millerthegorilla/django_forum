import pytest
from pytest_bdd import scenarios, then

from django_forum import models as forum_models

scenarios("../detail_comment.feature")


@then("The comment can be viewed")
def comment_can_be_viewed(page, test_comment):
    page.assert_text(test_comment.text)
