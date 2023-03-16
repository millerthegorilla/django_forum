def test_comment_delete(comment_delete, mocker, rf, mock_comment):
    m_c = mock_comment()
    comment_delete.object = m_c
    response = comment_delete.get_success_url()
    assert response == f"/post/{m_c.post_fk.id}/{m_c.post_fk.slug}/#thepost"
