"""
    _summary_
"""
from django import urls

from . import views as forum_views
from . import views_forum_post as forum_post_views

app_name = "django_forum"

postview_patterns = [
    urls.path("posts/", forum_post_views.PostList.as_view(), name="post_list_view"),
    urls.path(
        "post/<int:pk>/<slug:slug>/",
        forum_post_views.PostView.as_view(),
        name="post_view",
    ),
    urls.path(
        "create_post/", forum_post_views.PostCreate.as_view(), name="post_create_view"
    ),
    urls.path(
        "update_post/<int:pk>/<slug:slug>/",
        forum_post_views.PostUpdate.as_view(),
        name="post_update",
    ),
    urls.path(
        "delete_post/<int:pk>/<slug:slug>/",
        forum_post_views.PostDelete.as_view(),
        name="post_delete",
    ),
    urls.path(
        "report_post/<int:pk>/<slug:slug>/",
        forum_post_views.ReportPost.as_view(),
        name="post_report",
    ),
    urls.path(
        "create_comment/<int:pk>/<slug:slug>/",
        forum_post_views.CreateComment.as_view(),
        name="comment_create",
    ),
    urls.path(
        "delete_comment/<int:pk>/<slug:slug>/",
        forum_post_views.DeleteComment.as_view(),
        name="comment_delete",
    ),
    urls.path(
        "update_comment/<int:pk>/<slug:slug>/",
        forum_post_views.UpdateComment.as_view(),
        name="comment_update",
    ),
    urls.path(
        "report_comment/<int:pk>/<slug:slug>/",
        forum_post_views.ReportComment.as_view(),
        name="comment_report",
    ),
    urls.path("subscribe/", forum_post_views.subscribe, name="subscribe"),
]

urlpatterns = [
    urls.path(
        "profile/", forum_views.ForumProfile.as_view(), name="profile_update_view"
    ),
    urls.path(
        "update_avatar/", forum_views.UpdateAvatar.as_view(), name="update_avatar"
    ),
    urls.path("rules/", forum_views.RulesPageView.as_view(), name="rules_view"),
    urls.path("register/", forum_views.CustomRegister.as_view(), name="register"),
    # path('autocomplete/', autocomplete, name='autocomplete')  # experimental
    # autocomplete
] + postview_patterns

# the following goes in the project top level urls.py
# from django_profile.views import CustomRegister
# path('users/accounts/register/', CustomRegister.as_view(), name='register'),
