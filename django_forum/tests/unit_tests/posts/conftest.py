from dataclasses import dataclass
import pytest
import factory
from pytest_factoryboy import register
from faker import Faker

from django import utils
from django.db.models import base as django_db_base
from django.template import defaultfilters

from safe_imagefield.models import SafeImageField
from django_forum import models as forum_models
from django_forum import views_forum_post as forum_post_views


# @pytest.fixture()
# def get_post_request_data():
#     return {"title": ["first post"], "text": ["<p>first post again</p>"]}

fake = Faker()

POST_TEXT = "ipsum lorum dolem est"
POST_TITLE = "This is a test title"
USERNAME = "bob123"
DISPLAYNAME = "bob-holnes"
NUM_POSTS = 10


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
def render_mock(mocker):
    return mocker.patch("django_forum.views_forum_post.shortcuts.render")


@pytest.fixture()
def page_obj(mocker):
    pagination = mocker.patch("django_forum.views_forum_post.pagination")
    page_obj = mocker.MagicMock()
    pagination.Paginator.return_value.get_page.return_value = page_obj
    return page_obj


@dataclass
class PostDetails:
    pk: int
    username: str
    display_name: str
    text: str
    title: str
    slug: str
    created_at: utils.timezone
    get_absolute_url: str


def post_details():
    post_num = 1
    while post_num < NUM_POSTS:
        if post_num == 1:
            slug = defaultfilters.slugify(
                POST_TEXT[:10]
                + "-"
                + str(utils.dateformat.format(utils.timezone.now(), "Y-m-d H:i:s"))
            )
            yield PostDetails(
                pk=post_num,
                username=USERNAME,
                display_name=DISPLAYNAME,
                text=POST_TEXT,
                title=POST_TITLE,
                created_at=utils.timezone.now(),
                slug=slug,
                get_absolute_url="http://test1.com/" + str(post_num) + "/" + slug,
            )
        else:
            txt = fake.sentence(nb_words=30)
            slug = defaultfilters.slugify(
                txt[:10]
                + "-"
                + str(utils.dateformat.format(utils.timezone.now(), "Y-m-d H:i:s"))
            )
            yield PostDetails(
                pk=post_num,
                username=fake.user_name(),
                display_name=fake.user_name(),
                text=txt,
                title=fake.sentence(nb_words=10),
                created_at=fake.date_time(),
                slug=slug,
                get_absolute_url=fake.url() + str(post_num) + "/" + slug,
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
            slug=pd.slug,
            pk=pd.pk,
        )
        m_post.get_absolute_url = mocker.Mock(return_value=pd.get_absolute_url)
        return m_post

    return mock_post
