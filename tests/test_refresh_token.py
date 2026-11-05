from services import auth_settings


#1- verify login with valid refresh token
def test_valid_refresh_token(client, user, test_session):
    data= auth_settings.generate_reset_token(user)
    header={'access-token': data['access_token']}

    response= client.post('/auth/refresh', json= {}, headers= header)
    assert response.status_code == 200
    assert response.json()['access_token'] is not None
    

#2- verify login with invalid refresh token
'''def test_invalid_refresh_token(client, user, test_session):
    data= pass_settings.generate_tokens(user, test_session)
    header={'refresh-token': '2zdTB2MnE6D0kNSB.Jv5gvSlk_m32yet8D22JXJ7aVgylx9umxLcTOnC4MbOrqqGaPXcWTt-iAW8UEIOYxULlF1eW.X59WUddzurgaXyL8txM1fns6p4uqMuVB7VQ'}

    response= client.post('/auth/refresh', json= {}, headers= header)
    assert response.status_code == 200
    assert response.json()['access_token'] is None'''