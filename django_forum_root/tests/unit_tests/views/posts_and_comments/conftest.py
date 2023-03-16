from dataclasses import dataclass

import django
import factory
import pytest
from django import utils
from django.db.models import base as django_db_base
from django.template import defaultfilters
from faker import Faker
from pytest_factoryboy import register
from safe_imagefield.models import SafeImageField

from django_forum import models as forum_models
from django_forum import views_forum_post as forum_post_views

fake = Faker()

POST_TEXT = "ipsum lorum dolem est"
POST_TITLE = "This is a test title"
COMMENT_TEXT = "this is a test comment"
USERNAME = "bob123"
DISPLAYNAME = "bob-holnes"
NUM_POSTS = 10
MSG_TYPE = ""


@pytest.fixture()
def comment_text():
    return COMMENT_TEXT


@pytest.fixture()
def post_text_title():
    return (POST_TEXT, POST_TITLE)


@pytest.fixture()
def postlist_view():
    return forum_post_views.PostList()


@pytest.fixture()
def post_view():
    return forum_post_views.PostView()


@pytest.fixture()
def post_update():
    return forum_post_views.PostUpdate()


@pytest.fixture()
def post_delete():
    return forum_post_views.PostDelete()


@pytest.fixture()
def comment_create():
    return forum_post_views.CreateComment()


@pytest.fixture()
def comment_delete():
    return forum_post_views.DeleteComment()


@pytest.fixture()
def comment_update():
    return forum_post_views.UpdateComment()


@pytest.fixture()
def comment_report():
    return forum_post_views.ReportComment()


@pytest.fixture()
def post_report():
    return forum_post_views.ReportPost()


@pytest.fixture()
def redirect_mock(mocker):
    return mocker.patch("django_forum.views_forum_post.shortcuts.redirect")


@pytest.fixture()
def page_obj(mocker):
    pagination = mocker.patch("django_forum.views_forum_post.pagination")
    page_obj = mocker.MagicMock()
    pagination.Paginator.return_value.get_page.return_value = page_obj
    return page_obj


@dataclass
class MsgDetails:
    pk: int
    username: str
    text: str
    slug: str
    created_at: utils.timezone
    get_absolute_url: str
    display_name: str
    title: str


def msg_details():
    post_num = 1
    while post_num < NUM_POSTS:
        if post_num == 1:
            text = POST_TEXT
            title = POST_TITLE
            slug = defaultfilters.slugify(
                POST_TEXT[:10]
                + "-"
                + str(utils.dateformat.format(utils.timezone.now(), "Y-m-d H:i:s"))
            )
            username = USERNAME
            display_name = DISPLAYNAME
        else:
            text = fake.sentence(nb_words=30)
            title = fake.sentence(nb_words=4)
            slug = defaultfilters.slugify(
                text[:10]
                + "-"
                + str(utils.dateformat.format(utils.timezone.now(), "Y-m-d H:i:s"))
            )
            username = (fake.user_name(),)
            display_name = (fake.user_name(),)
        pd = MsgDetails(
            pk=post_num,
            username=username,
            text=text,
            created_at=utils.timezone.now(),
            slug=slug,
            get_absolute_url="http://test1.com/" + str(post_num) + "/" + slug,
            title=title,
            display_name=display_name,
        )
        yield pd
        post_num += 1


class PostFactory(factory.Factory):
    class Meta:
        model = forum_models.Post


register(PostFactory)


class CommentFactory(factory.Factory):
    class Meta:
        model = forum_models.Comment


register(CommentFactory)


@pytest.fixture()
def mock_post(request, mocker, mock_user, post_factory):
    post_gen = msg_details()

    def mock_message():
        pd = next(post_gen)
        m_u = mock_user()
        m_u.username = pd.username
        m_u.profile.display_name = pd.display_name
        m_msg = post_factory(
            author=m_u,
            text=pd.text,
            title=pd.title,
            created_at=pd.created_at,
            slug=pd.slug,
            pk=pd.pk,
        )
        m_msg.get_absolute_url = mocker.Mock(return_value=pd.get_absolute_url)

        return m_msg

    return mock_message


@pytest.fixture()
def mock_comment(request, mock_post, mocker, mock_user, comment_factory):
    post_gen = msg_details()

    def mock_message():
        pd = next(post_gen)
        m_u = mock_user()
        m_msg = comment_factory(
            author=m_u,
            text=pd.text,
            created_at=pd.created_at,
            slug=pd.slug,
            pk=pd.pk,
            post_fk=mock_post(),
        )
        m_msg.get_absolute_url = mocker.Mock(return_value=pd.get_absolute_url)

        return m_msg

    return mock_message
