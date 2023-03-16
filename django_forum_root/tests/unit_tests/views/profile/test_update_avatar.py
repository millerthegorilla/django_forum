def test_update_avatar(
    mock_user,
    rf,
    avatar_update,
    mocker,
):
    m_u = mock_user()
    request = rf.post("/update_avatar/")
    request.user = m_u
    avatar = mocker.MagicMock()
    mocker.patch.dict(request.FILES, {"avatar": avatar})
    update_avatar_model = mocker.patch.object(avatar_update, "model", autospec=True)
    update_avatar_model.objects.get.return_value = m_u.profile
    av_sav = m_u.profile.avatar.image_file.save = mocker.MagicMock()
    response = avatar_update.post(request)
    assert update_avatar_model.objects.get.call_count
    assert update_avatar_model.objects.get.call_args == mocker.call(profile_user=m_u)
    assert av_sav.call_count
    assert av_sav.call_args == mocker.call(avatar.name, avatar)
    assert response.status_code == 302
    assert response.url == avatar_update.success_url
