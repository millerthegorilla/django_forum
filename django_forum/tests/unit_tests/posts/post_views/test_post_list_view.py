import factory
import re
from faker import Faker
from pytest_factoryboy import register
import pytest
import uuid
from bs4 import BeautifulSoup
from dataclasses import dataclass
from unittest.mock import Mock, patch
from django_mock_queries.query import MockSet, MockModel

from django import http, utils, conf
from django.db.models import base as django_db_base
from django.template.defaultfilters import date

from safe_imagefield.models import SafeImageField
from django_forum import views_forum_post as forum_post_views
from django_forum import models as forum_models
from django_forum import forms as forum_forms

fake = Faker()

POST_TEXT = "ipsum lorum dolem est"
POST_TITLE = "This is a test title"
USERNAME = "bob123"
DISPLAYNAME = "bob-holnes"
NUM_POSTS = 10


@pytest.fixture()
def postlist_view():
    return forum_post_views.PostList()


@dataclass
class PostDetails:
    pk: int
    username: str
    display_name: str
    text: str
    title: str
    created_at: utils.timezone
    get_absolute_url: str


def post_details():
    post_num = 1
    while post_num < NUM_POSTS:
        if post_num == 1:
            yield PostDetails(
                pk=post_num,
                username=USERNAME,
                display_name=DISPLAYNAME,
                text=POST_TEXT,
                title=POST_TITLE,
                created_at=utils.timezone.now(),
                get_absolute_url="http://test1.com/",
            )
        else:
            yield PostDetails(
                pk=post_num,
                username=fake.user_name(),
                display_name=fake.user_name(),
                text=fake.sentence(nb_words=30),
                title=fake.sentence(nb_words=10),
                created_at=fake.date_time(),
                get_absolute_url=fake.url(),
            )
        post_num += 1


class PostFactory(factory.Factory):
    class Meta:
        model = forum_models.Post


register(PostFactory)


@pytest.fixture()
def mock_user(mocker):
    mock_profile = mocker.patch("django_forum.models.ForumProfile", autospec=True)
    mock_avatar = mocker.patch("django_forum.models.Avatar", autospec=True)
    mock_profile.return_value.avatar = mock_avatar
    mock_image_file = mocker.Mock(spec=SafeImageField)
    mock_user = mocker.patch("django.contrib.auth.models.User", autospec=True)
    mock_user._state = django_db_base.ModelState()
    type(mock_avatar).image_file = mocker.PropertyMock(return_value=mock_image_file)
    type(mock_profile).avatar = mocker.PropertyMock(return_value=mock_avatar)
    type(mock_profile).display_name = mocker.PropertyMock()
    type(mock_user).profile = mocker.PropertyMock(return_value=mock_profile)

    return mock_user


@pytest.fixture()
def mock_post(mocker, mock_user, post_factory):
    post_gen = post_details()

    def mock_post():
        pd = next(post_gen)
        mock_user.username = pd.username
        mock_user.profile.display_name.return_value = pd.display_name
        m_post = post_factory(
            author=mock_user,
            text=pd.text,
            title=pd.title,
            created_at=pd.created_at,
        )
        m_post.get_absolute_url = pd.get_absolute_url
        m_post.pk = pd.pk
        return m_post

    return mock_post


@pytest.mark.locutus()
def test_post_list_view_get_with_search(mocker, postlist_view, mock_post, rf, db):
    mocker.patch("sorl.thumbnail.shortcuts.get_thumbnail")
    pls = mocker.patch("django_forum.forms.PostListSearch", autospec=True)
    pls.return_value.is_valid.return_value = True
    pls.return_value.cleaned_data = {"q": "search terms"}
    pls.return_value["published"].value.return_value = ""
    pls.return_value.is_bound = True
    request = rf.get("/posts/")

    search_qs = MockSet()
    while True:
        try:
            search_qs.add(mock_post())
        except StopIteration:
            break
    search_qs.filter = search_qs
    search_qs.filter.filter.return_value = search_qs
    m_document_post = mocker.patch("django_forum.views_forum_post.forum_documents.Post")
    m_document_post.search.return_value.query.return_value.to_queryset.return_value = (
        search_qs
    )
    m_document_comment = mocker.patch(
        "django_forum.views_forum_post.forum_documents.Comment"
    )
    m_document_comment.search.return_value.query.return_value.to_queryset.return_value = (
        {}
    )

    response = postlist_view.get(request)

    pls.return_value.is_valid.assert_called_once()
    m_document_post.search.assert_called_once()
    m_document_comment.search.assert_called_once()
    assert POST_TEXT in response.content.decode()
    assert date(utils.timezone.now()) in response.content.decode()
    soup = BeautifulSoup(response.content, features="html.parser")
    assert (
        len(soup.body.findAll(attrs={"href": re.compile("http")}))
        == conf.settings.NUMPOSTS
    )
    assert (
        POST_TITLE
        in soup.findAll("a", attrs={"href": "http://test1.com/#thepost"})[0].text
    )


def test_post_list_view_get_no_search(request, postlist_view):
    pls = mocker.patch("django_forum.forms.PostListSearch", autospec=True)
    pls.return_value.is_valid.return_value = False
    request = rf.get("/posts/")
