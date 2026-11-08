import math
import os
import secrets
import dotenv
from services import http_responses, image_utils
from fastapi import responses, status, templating
from sqlalchemy.orm import Session
from post_dao import company_dao
from PIL import UnidentifiedImageError
from starlette.concurrency import run_in_threadpool


#loading env file
dotenv.load_dotenv()

#variables to send emails 
VERIFY_ACCOUNT= 'activate-user-account' 
FORGOT_PASSWORD= 'password-reset'
APP_NAME= 'Future Programmers'

#variables to user login access
JWT_SECRET: str | None= os.environ.get('jwt_secret')
JWT_ALGORITHM: str | None= os.environ.get('jwt_algo')
TOKEN_EXPIRE_MINUTES: int= 60
SECRET_KEY: str | None= os.environ.get('secret_key')
COOKIE_NAME= "Authorization"


# jinja2 setting template directory
templates= templating.Jinja2Templates(directory= "templates/pages")


# List options for total items per page
limit_items: list[int] = [1, 2, 10, 16]
total_items: int= 4


# variable to add user into session
sessions: dict = {}


# function to redirect user to index if login expired
async def login_expired():
    return responses.RedirectResponse(url="/?session_expired=True", status_code=status.HTTP_303_SEE_OTHER)



# function to get 3 top developers resumes to list on home page
async def get_ten_companies(db:Session):
    return await company_dao.get_random_companies(db)



# function to process developer image and company logo
async def process_img(directory, file, model_obj, db:Session):
    content= await file.read()

    if len(content) <= 0:
        return http_responses.status_406_not_acceptable("bi bi-person-fill-exclamation", 
                                                        "You must select a valid image!")

    try:
        # save new profile image
        new_img= await run_in_threadpool(image_utils.image_process, directory, content)
        
    except UnidentifiedImageError as error:
        return http_responses.status_400_bad_request("bi bi-camera-video-off", 
                                                    f"Couldn't process the image file. Try again! {error}")

    # get old image
    old_img= model_obj.Image

    # commit new profile image
    model_obj.Image= new_img
    model_obj.Img_Path= f"{directory / new_img}"

    db.commit()
    db.refresh(model_obj)

    # delete old profile image
    if old_img not in ["male.png", "female.png", "unisex.png"]:
        image_utils.image_deletion(old_img, directory, model_obj, db)

    return True



# generate random strig
def unique_string(byte: int= 8) -> str:
    return secrets.token_urlsafe(byte)


# function to add pagination
def pagination_settings(items_list, page, obj_class, items_per_page):
    if page < 1:
        page= page * -1

    start= (page - 1) * items_per_page
    end= start + items_per_page

    # setting the pagination
    if not items_list == None:
        pagination= {
            "cur_page": page,
            "items_found": len(items_list),
            "lenght": 0,
            "items_per_page": items_per_page, f"{obj_class}": items_list[start:end],
            "total": list(range(1, (math.ceil(len(items_list) / items_per_page) + 1)))
        }
        return pagination
    else:
        return None