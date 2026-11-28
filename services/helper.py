import math, os, secrets, dotenv
from sqlalchemy import func, select
from services import http_responses, image_utils
from fastapi import responses, status, templating
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
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
ALLOWED_LIMITS = {1, 2, 4, 6, 10, 16}


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
def global_data_pagination(data_source, page, item_per_page, db: Session):
    page= max(1, abs(page))

    if isinstance(data_source, list):
        data_set_total= len(data_source) 

    elif isinstance(data_source, Select):
        count= select(func.count()).select_from(data_source.order_by(None).subquery())
        data_set_total= db.scalar(count) or 0
    else: 
        data_set_total= db.scalar(select(func.count()).select_from(data_source)) or 0

    # return a empty list is there is not data found
    if data_set_total == 0:
        return []

    total_pages= math.ceil(data_set_total / item_per_page)
    page= min(page, total_pages)
    offset= (page - 1) * item_per_page

    if isinstance(data_source, list):
        data_set= data_source[offset : offset + item_per_page]

    elif isinstance(data_source, Select):
        paginate_query= data_source.offset(offset).limit(item_per_page)

        # if the query ismulte column we use mapping functio
        is_multi_column= (
            len(data_source.column_descriptions) > 1
            or data_source.column_descriptions[0].get("entity") is None
        )

        if is_multi_column:
            data_set= db.execute(paginate_query).mappings().all()
        else:
            data_set= db.scalars(paginate_query).unique().all()

    else:
        # fetching data for each page
        data_query= (
            select(data_source)
            .order_by(data_source.Created.desc())
            .offset(offset)
            .limit(item_per_page)
        )
        data_set= db.scalars(data_query).all()

        
    # dictionary return to populate HTML layout and paginate the data
    paginated_data={
        "data_set": data_set,
        "cur_page": page,
        "items_found": data_set_total,
        "items_per_page": item_per_page,
        "total": list(range(1, total_pages + 1)),
        "has_prev": page > 1,
        "has_next": page < total_pages
    }

    return paginated_data