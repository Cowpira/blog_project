from sqlalchemy import select
from data_model.models import Login_Errors_Track, Person, Password_Reset_Token
from services import helper, db_connection, http_responses, auth_settings
from routers import send_emails
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# if email and password is valid return the user
def authenticate_user(email: str, password: str, db: Session):
    # check if login is match with accounts in DB
    query= select(Person).where(Person.Email == email and Person.Active)
    user_found= db.execute(query).scalar()

    if not user_found:
        return http_responses.status_404_not_found("bi-envelope-slash-fill", "E-mail not Found!") 
    
    elif not user_found.Active:
        return http_responses.status_401_unauthorized("bi-person-fill-exclamation", "Your account need to be activated!")
    
    elif auth_settings.verify_pass(password, user_found.Password):
        # if user login sucessfully we delete all erros login
        delete_login_error(user_found, db)
        return user_found    
    else:
        return http_responses.status_406_not_acceptable("bi-envelope-at-fill", "Incorrect e-mail or password!") \
            if count_login_error(user_found, db) <= 5 \
            else http_responses.status_204_no_content("bi-hourglass-split", "You've exceed login limit!!")
    


# count number of login error
def count_login_error(user_found, db: Session):
    # find user by email
    query_login= select(Login_Errors_Track).where(Login_Errors_Track.user_id == user_found.Id)
    login_errors_found= db.execute(query_login).scalar()

    if not login_errors_found:
        add_login_error= Login_Errors_Track()
        add_login_error.Login_Tries = 1
        add_login_error.user_id= user_found.Id

        db.add(add_login_error)
        db.commit()
        db.refresh(add_login_error)
        return add_login_error.Login_Tries 
    else:
        login_errors_found.Login_Tries += 1

        db.commit()
        db.refresh(login_errors_found)
    
        return login_errors_found.Login_Tries 
    


# count number of login error
def delete_login_error(user_found, db: Session):
    # find user by email
    query_login= select(Login_Errors_Track).where(Login_Errors_Track.user_id == user_found.Id)
    login_errors_found= db.execute(query_login).scalar()

    if login_errors_found:
        login_errors_found.Login_Tries = 0

        db.commit()
        db.refresh(login_errors_found)



# generate jwt token and return as access token
def create_access_token(data: dict):
    to_encode= data.copy()

    expire= datetime.now(timezone.utc) + timedelta(minutes= helper.TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encode_jwt= jwt.encode(to_encode, helper.JWT_SECRET, algorithm= helper.JWT_ALGORITHM)
    return encode_jwt



# if user is authenticated we return the user object
async def get_current_user(request: Request, db: Session= Depends(db_connection.get_db)):
    token= request.cookies.get("access_token")
    credential_exception= http_responses.status_401_unauthorized("bi bi-x-octagon-fill", "Could not verify your credentials!")
   
    if token:
        try:
            payload= jwt.decode(token, helper.JWT_SECRET, algorithms=[helper.JWT_ALGORITHM])
            username: str= payload.get("sub")

            if username is None:
                raise credential_exception
        
            user_obj= await auth_settings.load_user(username, db)
            return user_obj
        except JWTError:
            credential_exception
    
    return None



# function to recover user account
async def find_user_account(url, data, bg_task, db: Session):
    obj_found= await auth_settings.load_user(data.get('email_address'), db)
   
    # if user found we delete all previos reset tokens
    if obj_found and obj_found.Active:
        # call function to delete previous token
        auth_settings.delete_previous_token(obj_found.Id, db)
        
        # calling function to generate a new reset password token
        token= await generate_save_new_token(obj_found.Id, db)

        # send email to reset password
        if await send_emails.recover_password_link(url, token, obj_found, bg_task) is ValueError:
            return http_responses.status_500_server_error("bi bi-envelope-slash-fill", "We couldn't send a recover link! \n Try again or contact the support")
        else:
            return http_responses.status_200_ok("bi bi-check2-circle", "Well done. \n Check your email and follow instructios to recover your account")  
    else:
       return http_responses.status_202_accepted("bi bi-envelope-paper-fill", "If an account is found, you'll receive instructions to reset your password")
   
    

# update_password
async def reset_password(email, data, bg_task, db: Session):
    query= select(Person).where(Person.Email== email)
    obj_found= db.execute(query).scalar()


    # verify if account is activated
    if obj_found and not obj_found.Active:
        return http_responses.status_401_unauthorized("bi-person-fill-exclamation", "Account not activated.\n Check your email or contact the support")
       
    elif not auth_settings.strong_password(data.get("password")):
        return http_responses.status_406_not_acceptable("bi bi-file-earmark-lock2-fill", "The password doesn't meet strong password requirements!")
    
    elif data.get("password") != data.get("conf_password"):
        return http_responses.status_406_not_acceptable("bi bi-signpost-split-fill", "'Password' doesn't match 'Confirm Password'!")
       
    else:
        #resetting user password into DB
        obj_found.Password= auth_settings.encrypt(data.get("password"))
        db.add(obj_found)
        db.commit()
        db.refresh(obj_found)

        #delete login errors
        delete_login_error(obj_found, db)

        #sending recover password email
        await send_emails.password_updated(obj_found, bg_task)
        auth_settings.delete_previous_token(obj_found.Id, db)
        return http_responses.status_200_ok("bi bi-check2-circle", "Password successfully updated")
    


# function to generate new token to activate users account or recover access
async def generate_save_new_token(user_id, db: Session):
    # then generate a new token to send 
    new_token= auth_settings.generate_reset_token()
    hash_token= auth_settings.hash_reset_token(new_token)
    expires_at= datetime.now(timezone.utc) + timedelta(minutes= helper.TOKEN_EXPIRE_MINUTES)

    # now we save the new token generate into DB
    reset_token= Password_Reset_Token(
        User_Id= user_id,
        Token_Hash= hash_token,
        Expires_At= expires_at
    )

    # now commit to DB
    db.add(reset_token)
    db.commit()

    return new_token
