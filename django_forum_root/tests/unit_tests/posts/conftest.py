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
def render_mock(mocker):
    return mocker.patch("django_forum.views_forum_post.shortcuts.render")


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
def mock_post(request, mocker, mock_user, post_factory):
    post_gen = msg_details()

    def mock_message():
        pd = next(post_gen)
        mock_user.username = pd.username
        mock_user.profile.display_name.return_value = pd.display_name
        m_msg = post_factory(
            author=mock_user,
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
def mock_comment(request, mocker, mock_user, comment_factory):
    post_gen = msg_details()

    def mock_message():
        pd = next(post_gen)
        mock_user.username = pd.username
        mock_user.profile.display_name.return_value = pd.display_name
        m_msg = comment_factory(
            author=mock_user,
            text=pd.text,
            created_at=pd.created_at,
            slug=pd.slug,
            pk=pd.pk,
        )
        m_msg.get_absolute_url = mocker.Mock(return_value=pd.get_absolute_url)

        return m_msg

    return mock_message
