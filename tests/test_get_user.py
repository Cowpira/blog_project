#1- test fetching user data if authenticated
from services.authentication import create_access_token

def test_fetch_user(client, verified_user):
    data= create_access_token(verified_user)

    header= {'Authorization': f'Bearer {data["access_token"]}'}

    response= client.get('/user/me', headers= header)
    assert response.status_code == 200
    assert response.json()['Email'] == verified_user.Email


#2- test fetching user data with invalid token
def test_fetch_user_invalid_token(client, verified_user, test_session):
    data= create_access_token(verified_user)

    header= {'Authorization': f'Bearer {data["access_token"][:-6]}shke82'}

    response= client.get('/user/me', headers= header)
    assert response.status_code == 401
    assert 'Ssn' not in response.json()
    assert 'Email' not in response.json()


#3- test fetching user by user ID (primary key)
def test_fetch_user_by_pk(authorized_client, verified_user):
    response= authorized_client.get(f'/user/{verified_user.Id}')
    assert response.status_code == 200
    assert response.json()['Email'] == verified_user.Email