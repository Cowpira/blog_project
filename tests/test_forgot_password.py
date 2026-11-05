

#1- sending forget password recorver link
def test_forget_password(client, verified_user):
    response= client.post('/auth/forgot-password', json= {'Email': verified_user.Email})
    assert response.status_code == 200


#2- check if email is valid to send recover password link
def test_invalid_email(client):
    response= client.post('auth/forgot-password', json={'Email': 'test_invalidgmail.com'})
    assert response.status_code == 422


#3- check if user is verified to request recover link
def test_unverified_user_request_recover_password(client, unverified_user):
    response= client.post('/auth/forgot-password', json={'Email': unverified_user.Email})
    assert response.status_code == 403


#4- check if user is active to request recover link
def test_active_request_recover_password(client, unverified_user):
    response= client.post('/auth/forgot-password', json={'Email': unverified_user.Email})
    assert response.status_code == 403