def test_report_post(mocker, post_report, rf, mock_user, mock_post):
    m_p = mock_post()
    m_p_save = mocker.patch.object(m_p, "save")
    m_u = mock_user()
    request = rf.post(f"/report_post/{m_p.id}/{m_p.slug}/")
    request.user = m_u
    post_report.request = request
    g_o = mocker.patch.object(post_report, "get_object")
    g_o.return_value = m_p
    mock_task = mocker.patch("django_forum.views_forum_post.tasks.async_task")
    response = post_report.post()
    assert response.status_code == 302
    assert response.url == f"/post/{m_p.id}/{m_p.slug}/"
    assert m_p_save.call_count == 1
    assert m_p_save.call_args == mocker.call(
        update_fields=["moderation_date", "commenting_locked"]
    )
    assert mock_task.call_count == 1
    assert mock_task.call_args[0][0] == post_report.task
    assert mock_task.call_args[1] == {"type": "Post"}
