from services import helper, auth_settings
from data_model.models import User


NEW_PASSWORD= 'Celio1981#19'
test_case: bool

def generate_token(user: User):
    string_ctx= user.get_context_str(context= helper.FORGOT_PASSWORD)
    return auth_settings.encrypt(string_ctx)


def get_data(user):
    data= {
        'Token': generate_token(user),
        'Email': user.Email,
        'Password': NEW_PASSWORD
    }
    return data


#1- verify if user can reset password
def test_reset_password(client, verified_user):
    data= get_data(verified_user)

    response= client.put('/auth/reset-password', json= data)
    assert response.status_code == 200
    test_case= True
    check_password_reseted(data, client, verified_user, test_case)


#2- verify reset password with invalid token 
def test_reset_without_token(client, verified_user):
    data= get_data(verified_user)
    data.update(Token= 'dtsrygf2xiygudfjSUjhgcg47JH')

    response= client.put('/auth/reset-password', json= data)
    assert response.status_code == 404
    
    test_case= False
    check_password_reseted(data, client, verified_user, test_case)


#3- verify reset password with invalid email
def test_reset_invalid_email(client, verified_user):
    data = get_data(verified_user)
    data.update(Email= 'deliverydeliveryti.com')

    response= client.put('/auth/reset-password', json= data)
    assert response.status_code == 422
    test_case= False
    check_password_reseted(data, client, verified_user, test_case)


#4- verify reset password with any email and valid token
def test_reset_any_email(client, verified_user):
    data = get_data(verified_user)
    data.update(Email= 'macmiller.app@gmail.com')

    response= client.put('/auth/reset-password', json= data)
    assert response.status_code == 404
    test_case= False
    check_password_reseted(data, client, verified_user, test_case)


#testing if the password was reset correctly
def check_password_reseted(data, client, verified_user, case):
    del data['Token']
    del data['Email']
    data['username']= verified_user.Email
    data['password']= NEW_PASSWORD

    login_test= client.post('/auth/login', data= data)

    if case:
        assert login_test.status_code == 200
    else:
        assert login_test.status_code != 200
