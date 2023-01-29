import pytest
import uuid
from unittest.mock import PropertyMock
from django_forum import models as forum_models
from django_forum import views as forum_views
from django_forum import views_forum_post as forum_post_views
from django_forum import forms as forum_forms


@pytest.mark.locutus()
def test_post_create_get_context_data_no_form(mocker):
    mocker.patch(
        "django_forum.views_forum_post.PostCreate.form_class",
        new_callable=PropertyMock,
    )
    pc_view = forum_post_views.PostCreate()
    response = pc_view.get_context_data()
    assert type(response) == dict
    forum_post_views.PostCreate.form_class.assert_called_once()
