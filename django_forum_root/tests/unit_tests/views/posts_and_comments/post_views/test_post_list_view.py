import re
import uuid

import pytest
from django import conf, http, utils
from django.template.defaultfilters import date
from django_mock_queries.query import MockModel, MockSet
from pytest_factoryboy import register

from django_forum import forms as forum_forms
from django_forum import models as forum_models
from django_forum import views_forum_post as forum_post_views


def test_post_list_view_get_with_search(
    mocker, postlist_view, mock_post, rf, post_text_title, render_mock, page_obj
):
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

    postlist_view.get(request)

    pls.return_value.is_valid.assert_called_once()
    m_document_post.search.assert_called_once()
    m_document_comment.search.assert_called_once()
    render_mock.assert_called_once_with(
        request,
        postlist_view.template_name,
        {
            "form": pls(),
            "page_obj": page_obj,
            "search": 9,
            "is_a_search": True,
            "site_url": "http://testserver",
        },
    )


def test_post_list_view_get_no_search(
    request, postlist_view, mocker, rf, render_mock, page_obj
):
    pls = mocker.patch("django_forum.forms.PostListSearch", autospec=True)
    pls.return_value.is_valid.return_value = False
    request = rf.get("/posts/")
    postlist_view.get(request)
    pls.return_value.is_valid.assert_called_once()
    render_mock.assert_called_once_with(
        request,
        postlist_view.template_name,
        {
            "form": pls(),
            "page_obj": page_obj,
            "search": 0,
            "is_a_search": False,
            "site_url": "http://testserver",
        },
    )
