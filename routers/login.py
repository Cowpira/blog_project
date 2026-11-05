import random
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from services import authentication, http_responses, auth_settings, helper
from services.db_connection import get_db
from fastapi import APIRouter, BackgroundTasks, Depends, Request, responses, status
from post_dao import developers_dao, message_dao
from data_model.models import Developer, Employee
from data_model.schemas import Login, Password_Reset, Recover_Password
from typing import Annotated
from slowapi import Limiter
from slowapi.util import get_remote_address

# user api routers
public_api= APIRouter()


# setting the slowAPI request limiter 
limiter= Limiter(key_func= get_remote_address, storage_uri= "redis://localhost:6379/0")

# function to create a session list and add the user loged-in into it
def create_session(user_id: int):
    session_id = len(helper.sessions) + random.randint(0, 1000000)
    helper.sessions.update([(session_id, user_id)])
    return session_id



# function to load data for index page
async def load_index_page(request, cur_user, result, db):
    developers= await developers_dao.get_random_developers(db)
    companies= await helper.get_ten_companies(db)
    
    return helper.templates.TemplateResponse('index.html', {'request': request, 'user_in': cur_user, 'result': result, 
                                                            'users': developers, 'companies': companies, 'total_items':helper.total_items})



@public_api.post('', include_in_schema=True, response_model= Login, status_code= status.HTTP_200_OK)
async def login(request: Request, db: Annotated[Session, Depends(get_db)], 
                data: OAuth2PasswordRequestForm= Depends()):
    
    url_data= await request.form()
    # getting current url and remove previous parameter
    cur_url= url_data.get("cur_url").split("error_code")[0]
   
    # verify user credentials
    user__in= authentication.authenticate_user(data.username.lower(), data.password, db)
  
    if isinstance(user__in, (Developer, Employee)):
        # create user loged in JWT token access
        access_token= authentication.create_access_token({"sub": user__in.Email})

        # calling method to create a session id
        session_id= create_session(user__in.Id)
        
        # update user total messages when he/her login Employee or Developer
        await message_dao.update_total_messages(user__in, db)

        # setting a cook to store user session
        if access_token:
            response= responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
            response.set_cookie(key="session_id", value=session_id, httponly=True)
            response.set_cookie(key= "access_token", value= access_token, httponly=True)

            return response
        else:
            error_msg= 'Could not verify the access token!'
            error_icon= 'bi-person-fill-lock'

            cur_url= cur_url+ (f"&error_code=204&error_icon={error_icon}&error_msg={error_msg}&email={data.username.lower()}" \
                            if "?" in cur_url else f"?error_code=204&error_icon={error_icon}&{error_msg}&email={data.username.lower()}")
            
            return responses.RedirectResponse(url=f"{cur_url}", status_code=status.HTTP_303_SEE_OTHER)
    else:
        cur_url= cur_url+ (f"&error_code={user__in.status_code}&error_icon={user__in.detail[0]}&error_msg={user__in.detail[1]}&email={data.username.lower()}" \
                        if "?" in cur_url else f"?error_code={user__in.status_code}&error_icon={user__in.detail[0]}&error_msg={user__in.detail[1]}&email={data.username.lower()}")
        
        return responses.RedirectResponse(url=f"{cur_url}", status_code=status.HTTP_303_SEE_OTHER)



# function to verify user account
@public_api.get("/verifying_user/{user_email}&{token}", include_in_schema= False, status_code=status.HTTP_200_OK)
async def verifying_user(request: Request, user_email: str, token: str, db: Annotated[Session, Depends(get_db)]):

    # verify if reset token is valid
    hash_token= await auth_settings.validate_reset_token(token, db)
        
    # check if token expired
    if not hash_token or hash_token.Expires_At.replace(tzinfo=(timezone.utc)) < datetime.now(timezone.utc):
        # delete previous token is expired
        # pass_settings.delete_previous_token(user_id, db)

        result= http_responses.status_406_not_acceptable("bi bi-clock-history", "Invalid Token or expired. Try to reset your password again")
        return helper.templates.TemplateResponse("account_not_found.html", {'request': request, 'result': result})
   
    else:
        # if token is valid redirect user to reset password
        return helper.templates.TemplateResponse("verifying_user.html", {'request': request, 'result': "", 'user_email': user_email})
   


# function to redirect user to reset password page
@public_api.get("/reset-password/{user_email}", include_in_schema=False)
def reset_password(request: Request, user_email: str):
    return helper.templates.TemplateResponse("reset_password.html", {'request': request, 'user_email': user_email, 'result': ""})


# function to update users password
@public_api.post("/reset-password/{user_email}", include_in_schema= False, response_model=Password_Reset, status_code=status.HTTP_200_OK)
@limiter.limit("1/hour") # limit 1 reset password request per hour
async def reset_password(request: Request, user_email: str, bg_task: BackgroundTasks, db: Annotated[Session, Depends(get_db)]):
    # calling function to reset user password
    result= await authentication.reset_password(user_email, await request.form(), bg_task, db)
    return helper.templates.TemplateResponse("reset_password.html", {'request': request, 'result': result})
    


# function to request recover password
@public_api.post('/find_account', include_in_schema= False, response_model=Recover_Password, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/hour")  # limit 5 find account request per hour
async def find_account(request: Request, bg_task: BackgroundTasks, db: Annotated[Session, Depends(get_db)]):

    result= await authentication.find_user_account(request.url_for, await request.form(), bg_task, db)
    
    return await load_index_page(request, None, result, db)