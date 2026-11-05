from tests.conftest import PASSWORD


#1- Test user login
def test_user_login(client, verified_user):
    response= client.post('/auth/login', data={'username': verified_user.Email, 'password': PASSWORD})

    assert response.status_code == 200
    print(response.content)
    assert response.json()['access_token'] is not None
    assert response.json()['expires_in'] is not None


#2- Test login with incorrect Email
def test_incorrect_email(client, user):
    response= client.post('/auth/login', data={'username': 'wrong_email@icloud.com', 'password': user.Password})
    assert response.status_code == 404
    

#3- Test login with incorrect password
def test_incorrect_password(client, user):
    response= client.post('/auth/login', data={'username': user.Email, 'password': 'wrong_pass'})
    assert response.status_code == 404
    assert response.json()['detail'] == 'User credentials are invalid!'


#4- Test unregistered user
def test_unregistered_user(client, unverified_user):
    response= client.post('/auth/login', data={'username': unverified_user.Email, 'password': unverified_user.Password})
    response.status_code == 400


#5- Test unverifies user
def test_unverified_user(client, unverified_user):
    response= client.post('/auth/login', data= {'username': unverified_user.Email, 'password': unverified_user.Password})
    response.status_code == 400
