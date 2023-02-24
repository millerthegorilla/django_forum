import pytest
from django_mock_queries.query import MockSet


def test_form_valid(mocker, post_update, mock_post):
    mp = mock_post()
    form = mocker.patch("django_forum.forms.Post", autospec=True)
    form.save.return_value = mp
    response_json = post_update.form_valid(form)
    assert form.save.call_count == 1
    assert response_json.status_code == 200


@pytest.mark.locutus
def test_form_invalid(mocker, post_update, mock_post, render_mock, rf):
    mp = mock_post()
    request = rf.post(
        f"update_post/{mp.pk}/{mp.slug}/",
        {"slug": mp.slug, "data": "false"},
        **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"},
    )
    type(post_update).request = mocker.PropertyMock(return_value=request)
    type(post_update).object = mocker.PropertyMock(return_value=mp)
    type(mp).comments = mocker.PropertyMock(return_value=MockSet())
    form = mocker.patch("django_forum.forms.Post", autospec=True)
    post_update.form_invalid(form)
    breakpoint()
