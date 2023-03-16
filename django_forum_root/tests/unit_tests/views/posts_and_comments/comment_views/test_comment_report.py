def test_comment_report(mock_user, rf, mock_comment, mocker, comment_report):
    m_c = mock_comment()
    m_c_save = mocker.patch.object(m_c, "save")
    request = rf.post(f"/report_comment/{m_c.id}/{m_c.slug}/")
    request.user = mock_user()
    comment_report.request = request
    mock_task = mocker.patch("django_forum.views_forum_post.tasks.async_task")
    g_o = mocker.patch.object(comment_report, "get_object")
    g_o.return_value = m_c
    response = comment_report.post()
    assert response.status_code == 302
    assert response.url == f"/post/{m_c.post_fk.id}/{m_c.post_fk.slug}/#{m_c.slug}"
    assert m_c_save.call_count == 1
    assert m_c_save.call_args == mocker.call(update_fields=["moderation_date"])
    assert mock_task.call_count == 1
    assert mock_task.call_args[0][0] == comment_report.task
    assert mock_task.call_args[1] == {"type": "Comment"}
