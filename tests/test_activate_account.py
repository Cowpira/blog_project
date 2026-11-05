from services import helper, auth_settings
from data_model.models import User


def setting_token(user_param):
    string_context= user_param.get_context_str(context= globals.USER_VERIFY_ACCOUNT)
    token= auth_settings.PassEncrypt(string_context)

    data= {
        'Token': token,
        'Email': user_param.Email
    }
    return data


#1- Test if user account action works
def test_account_activation(client, unverified_user, test_session):
    
    response= client.post('/user/activate-account', json= setting_token(unverified_user))
    assert response.status_code == 200

    activating_user= test_session.query(User).filter(User.Ssn == unverified_user.Ssn).first()
    assert activating_user.Activated is True
    assert activating_user.Activated_Date is not None


#2- Test if activation link is valid only once
def test_activate_twice(client, unverified_user):
    data = setting_token(unverified_user)

    response= client.post('/user/activate-account', json= data)
    assert response.status_code == 200

    #sending the activation request again
    response= client.post('/user/activate-account', json= data)
    assert response.status_code != 200


#3- Test if invalid token fails
def test_invalid_token(client, user, test_session):
    data={
        'Token': 'fgdfjfhgjfgfghjhgsehgjfgfj',
        'Email': user.Email
    }

    response= client.post('/user/activate-account', json= data)
    assert response.status_code != 200

    activating_user= test_session.query(User).filter(User.Email == user.Email).first()
    assert activating_user.Activated is False
    assert activating_user.Activated_Date is None


#4- Test if invalid email fails
def test_invalid_email(client, unverified_user, test_session):
    data= setting_token(unverified_user)
    data.update(Email= 'noreply@terra.com')

    response= client.post('/user/activate-account', json= data)
    assert response.status_code != 200

    activating_user= test_session.query(User).filter(User.Email == unverified_user.Email).first()
    assert activating_user.Activated is False
    assert activating_user.Activated_Date is not None