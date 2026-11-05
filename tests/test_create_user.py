from services import globals
from tests.conftest import FIRST_NAME, LAST_NAME, ADDRESS, EMAIL, PASSWORD, PHONE

data={
    'First_Name': FIRST_NAME,
    'Last_Name': LAST_NAME,
    'Address': ADDRESS,
    'Email': EMAIL,
    'Password': PASSWORD,
    'Phone': PHONE,
    'Activated': False,
    'Created': globals.Cur_Date()
}

# 1- test adding a new user into DB
def test_add_user(client):
    response= client.post('/users/create-account', json= data)
    assert response.status_code == 201
    assert 'password' not in response.json()


# 2- test adding existing SSN
def test_exiting_ssn(client, user):
    response= client.post('/users', json= data.update(SSN= user.Ssn))
    assert response.status_code != 201


# 3- test adding existing EMAIL
def test_existing_email(client, user):
    response= client.post('users', json= data.update(EMAIL= user.Email))
    assert response.status_code != 201

# 4- test adding an in calid EMAIL
def test_invalid_email(client):
    response= client.post('/users', json= data.update(EMAIL= 'test_invalid.com'))
    assert response.status_code != 201


# 5- test adding user with empty SSN
def test_empty_ssn(client):
    response= client.post('/users', json= data.update(SSN= ''))
    assert response.status_code != 201


# 6- test if empty EMAIL is detected
def test_empty_email(client):
    response= client.post('/users', json= data.update(EMAIL= ' '))
    assert response.status_code != 201


# 7- test if empty PASSWORD is detected
def test_empty_password(client):
    response= client.post('/user/', json= data.update(PASSWORD= ''))
    assert response.status_code != 201


#8- test if PASSWPRD straght is detected for numeric only
def test_numeric_password(client):
    response= client.post('/user/', json= data.update(PASSWORD= '1290345'))
    assert response.status_code != 201


#9- Test if PASSWPRD straght is detected for char only
def test_char_password(client):
    response= client.post('/user/', json= data.update(PASSWORD= 'celiomiller#100'))
    assert response.status_code != 201


#10- Test if PASSWPRD straght is detected for lower char only
def test_lower_password(client):
    response= client.post('/user/', json= data.update(PASSWORD= 'celio#100'))
    assert response.status_code != 201


#11- Test if PASSWPRD straght is detected for capital char only
def test_upper_password(client):
    response= client.post('/user/', json= data.update(PASSWORD= 'CELIO#100'))
    assert response.status_code != 201
