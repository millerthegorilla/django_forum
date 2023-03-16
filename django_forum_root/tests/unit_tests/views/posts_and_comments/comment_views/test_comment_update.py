def test_comment_update(
    render_mock, mock_user, rf, mock_comment, comment_text, comment_update, mocker
):
    m_c = mock_comment()
    m_u = mock_user()
    request = rf.post(f"/update_comment/{m_c.id}/{m_c.slug}/")
    request.POST = {"author": m_u.username, "text": comment_text}
    comment_update.kwargs = {"pk": m_c.id, "slug": m_c.slug}
    m_u = mocker.patch("django_forum.forms.User")
    m_u.objects.return_value.get.return_value = m_u
    g_o = mocker.patch.object(comment_update, "get_object")
    g_o.return_value = m_c
    comment_update.request = request
    response = comment_update.post(request)
    assert response.status_code == 200
