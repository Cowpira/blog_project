import time, uuid
from fastapi import BackgroundTasks, Depends, FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from services import db_connection, helper, http_responses
from services.authentication import get_current_user
from data_model.models import Person
from routers import company, developers, employeer, login, post, jobs, answer, message, reply, send_emails
from post_dao import person_dao
from sqlalchemy.orm import Session
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware


# instance of the fastAPI routers
app = FastAPI()
limiter= login.limiter
app.state.limiter= limiter


# URLs called from frontend pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:3000"]
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# mounting files path to static folder access
app.mount("/static", StaticFiles(directory="static"), name="static")
# mounting files path to uploaded images (developer profile & company logo)
app.mount("/uploaded_dev_images", StaticFiles(directory="uploaded_dev_images"), name="uploaded_dev_images")
app.mount("/uploaded_comp_images", StaticFiles(directory="uploaded_comp_images"), name="uploaded_comp_images")
app.add_middleware(SessionMiddleware, secret_key= helper.SECRET_KEY)


# Implemented and added custom middleware to FastAPI
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    
    return response


# check if session id is valid
def get_session_id(request: Request):
    session_id= request.cookies.get("session_id")
    return session_id

 
# function to slowAPI exction handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exeption_handler(request:Request, exc: RateLimitExceeded):
    current_path = request.url.path
    result= http_responses.status_429_limit_request(current_path)

    return helper.templates.TemplateResponse('limit_request.html', {'request': request, 'result': result, 
                                                                    'user_in': ''})


# router to index page
@app.get('/', include_in_schema=False)
@app.get('/home', include_in_schema=False, name='home')
async def home(request: Request, db: Session= Depends(db_connection.get_db), 
               cur_user: Person= Depends(get_current_user)):

    return await login.load_index_page(request, cur_user, '', db)



# router to index page if user is authenticated
@app.get('/contact', include_in_schema=False)
async def contact_page(request: Request, cur_user: Person= Depends(get_current_user)):
    
    return helper.templates.TemplateResponse('contact.html', {'request': request, 'result': '', 'user_in': cur_user})

@app.post('/contact', include_in_schema=False)
@limiter.limit("5/hour")  # limit 5 POST request per hour
async def contact(request: Request, bg_task: BackgroundTasks, cur_user: Person= Depends(get_current_user)):
    data= await request.form()

    #send email from user contact
    if await send_emails.user_contact(data, bg_task):
        result= http_responses.status_200_ok("bi bi-check2-circle", f"{data.get('first_name')} your message was sent. Thanks.")
    else:
        result= http_responses.status_500_server_error("bi bi-send-exclamation-fill", "your message couldn't be sent. Try again later.")
    
    return helper.templates.TemplateResponse('contact.html', {'request': request, 'user_in': cur_user, 'result': result})



# router to index page if user is authenticated
@app.get('/help', include_in_schema=False)
def help_page(request: Request, cur_user: Person= Depends(get_current_user)):
    return helper.templates.TemplateResponse('help.html', {'request': request, 'user_in': cur_user, 'result': ''})



# function to activate developer account
@app.get("/request_activate_account/{user_id}&{token}")
@limiter.limit("3/hour") # limit 3 activate account request per hour
async def request_activate_account(request: Request, user_id: uuid.UUID, token: str, bg_task: BackgroundTasks, 
                           db: Session= Depends(db_connection.get_db)):
    
    result= await person_dao.activate_users_account(user_id, token, bg_task, db)
    return helper.templates.TemplateResponse("activate_account.html", {'request': request, 'result': result})



# method to log user out of the session
@app.get("/logout", include_in_schema=False)
async def logout(request: Request, response: Response, cur_user: Person= Depends(get_current_user),
    db: Session= Depends(db_connection.get_db)):

    helper.sessions.clear()
    result= http_responses.status_202_accepted("bi bi-person-fill-lock", "Thanks for choosing Future Programmers <br> Hope you back soon")
    response= await login.load_index_page(request, None, result, db)

    # removing the session from the list and cookies
    response.delete_cookie(key= "access_token", path='/')
    response.delete_cookie(key= "session_id", path='/')

    return response



# handeling routers that does not exit
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return helper.templates.TemplateResponse("error_page.html", {'request': request, 'result': exc}) 


######################################################################################################################
###########################################  FUTURE PROGRAMMERS ROUTERS ##############################################
# app routers
app.include_router(login.public_api, tags=['Auth'], prefix='/login')


# ROUTER FOR SEARCH USERS OR POSTS
app.include_router(developers.search_dev, tags=['Search'], prefix='/search_dev')
app.include_router(post.search_post_api, tags=['Search'], prefix='/search_post')


# ROUTER FOR UNAUTHENTICATED USERS
app.include_router(employeer.public_api, tags=['Public'], prefix='/employeer')
app.include_router(developers.public_api, tags=['Public'], prefix='/users')
app.include_router(post.public_api, tags=['Public'], prefix='/posts')
app.include_router(jobs.public_api, tags=['Public'], prefix='/jobs')


# ROUTER FOR AUTHENTICATED USERS
app.include_router(employeer.restrict_api, tags=['LogedIn'], prefix='/restricted', dependencies= [Depends(get_current_user)])
app.include_router(company.restrict_api, tags=['LogedIn'], prefix='/restricted', dependencies=[Depends(get_current_user)])
app.include_router(developers.restrict_api, tags=['LogedIn'], prefix='/restricted', dependencies=[Depends(get_current_user)])
app.include_router(post.restrict_api, tags=['LogedIn'], prefix='/restricted', dependencies=[Depends(get_current_user)])
app.include_router(jobs.restrict_api, tags=['LogedIn'], prefix='/restricted', dependencies= [Depends(get_current_user)])
app.include_router(reply.restrict_api, tags=['LogedIn'], prefix='/restricted', dependencies= [Depends(get_current_user)])
app.include_router(message.restrict_api, tags=['LogedIn'], prefix='/restricted', dependencies= [Depends(get_current_user)])
app.include_router(answer.restrict_api, tags=['LogedIn'], prefix='/restricted', dependencies= [Depends(get_current_user)])