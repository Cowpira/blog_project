import os
import uuid
from fastapi import APIRouter, Depends, Request, status, UploadFile, BackgroundTasks
from services import helper, http_responses, image_utils
from services.db_connection import get_db
from services.authentication import get_current_user
from routers.login import limiter
from data_model.models import Developer, Employee
from data_model.schemas import New_Developer, Dev_Response
from post_dao import developers_dao, jobs_dao, portfolio_dao
from sqlalchemy.orm import Session


# user api routers global variables
public_api= APIRouter()
restrict_api= APIRouter()
search_dev= APIRouter()


##############################################################################################################################
########################################## GLOBALS FUNCTIONS FOR ALL ROUTERS FILES  ##########################################

# function to direc developer to 'my_account' page
async def load_my_dev_account(request, result, cur_user, db):
    if not cur_user:
        return await helper.login_expired()
    
    return helper.templates.TemplateResponse("my_dev_account.html", 
                                            {'request': request, 'user_in': cur_user, 'result': result,
                                            'resume': await portfolio_dao.resume_by_dev_id(cur_user.Id, db)})


# function to paginate developers and return HTML page
async def developers_page_destination(request, search_dev, page, items_per_page, cur_user, result, db):
    null_search = False

    # getting all developer and their resume
    if search_dev:
        user_list= await developers_dao.search_user(search_dev, db)
        
        if not user_list:
            null_search= True
            user_list= await developers_dao.list_users(db)
    else:
        user_list= await developers_dao.list_users(db)


    paginated_users= helper.pagination_settings(user_list, page, 'user', items_per_page)
    return helper.templates.TemplateResponse("users.html", 
                                              {'request': request, 'user_in': cur_user, 'search': search_dev, 'null_search': null_search,
                                               'result': result, 'users': paginated_users, 'limit_items': helper.limit_items,
                                               'website_url': os.environ.get("website_url")})


##############################################################################################################################
############################################### PUBLIC FUNCTIONS FOR ALL USERS  ##############################################

# function to list all developers
@public_api.get('', response_model=list[Dev_Response], include_in_schema= False)
async def users(request: Request, list: int=0, page: int= 1, db: Session= Depends(get_db), 
                cur_user: Developer= Depends(get_current_user)):
        
    if list and list >= 1:
        helper.total_items= list
            
    return await developers_page_destination(request, None, page, helper.total_items, cur_user, None, db)
    


# function to list developers found
@search_dev.get('', response_model=list[Dev_Response], include_in_schema= False)
async def search_developer(request: Request, search_dev: str, page: int= 1, db: Session= Depends(get_db), 
                        cur_user: Developer= Depends(get_current_user)):
    # getting search parameter
    search_dev= request.query_params.get('search_dev')
    return await developers_page_destination(request, search_dev, page, helper.total_items, cur_user, None, db)
     


# function to create and save a new developer
@public_api.get('/', response_model=New_Developer, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def add_developer(request: Request):
    return helper.templates.TemplateResponse("create_developer_account.html", {'request': request, 'result': "", 'data': None})

@public_api.post('/', response_model=Dev_Response, status_code= status.HTTP_200_OK)
@limiter.limit("1/day") # limit create 1 developer account per day
async def add_developer(request: Request, bg_task: BackgroundTasks, db: Session= Depends(get_db)):
    
    if request.query_params.get('new_user'):
        dev_data= await request.form()
        result= await developers_dao.create_user(dev_data, request.url_for, bg_task, db)
    
    if result:
        response= http_responses.status_200_ok("bi bi-person-badge", 
                                            f"Welcome to Future Programmers <br> Follow instructios in the e-mail to activate your account")
        developers= await developers_dao.get_random_developers(db)
        return helper.templates.TemplateResponse('index.html', context= {'request': request, 'user_in': '', 'result': response, 'users': developers})
    else:   
        response= http_responses.status_503_service_unavailable("bi bi-send-exclamation-fill", 
                                                                                 f"Account created but couldn't send activation link <br> Contact support to activate your account!")
        return helper.templates.TemplateResponse("create_developer_account.html", 
                                                  {'request': request, 'data': dev_data, 'result': response })
        
    

################################################################################################################
################################ RESTRICTED FUNCTIONS FOR LOGGED IN DEVELOPERS  ################################

# function to save developer portfolio
@restrict_api.post('/add_portfolio', include_in_schema= False)
async def add_portfolio(request: Request, db: Session= Depends(get_db), 
                        cur_user: Developer= Depends(get_current_user)):

    if cur_user:
        result= await portfolio_dao.save_portfolio(await request.form(), cur_user, db)
        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await helper.login_expired()



# function to update developers data
@restrict_api.post('/dev_account/update_my_data', include_in_schema= False)
#@limiter.limit("5/hour") # limit 5 update developer data per hour
async def update_my_data(request: Request, db: Session= Depends(get_db), 
                         cur_user: Developer= Depends(get_current_user)):
    
    if cur_user:
        result= await developers_dao.update_developer(await request.form(), cur_user, db)
        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await helper.login_expired()



# function to list developer modal resume
@restrict_api.get('/dev_resume_modal/{dev_id}', include_in_schema= False)
async def dev_resume_modal(request: Request, dev_id: uuid.UUID, cur_emp: Employee= Depends(get_current_user),
                           db: Session= Depends(get_db)):
    if cur_emp:
        # getting developer and its resume by ID
        dev_found= await developers_dao.developer_by_id(dev_id, db)
        dev_resume= await portfolio_dao.resume_by_dev_id(dev_id, db)

        # extracting each model from resume list
        edu= dev_resume.get("education") if isinstance(dev_resume, dict) else getattr(dev_resume, "education", None)
        cert= dev_resume.get("certifications") if isinstance(dev_resume, dict) else getattr(dev_resume, "certifications", None)
        front= dev_resume.get("front_end") if isinstance(dev_resume, dict) else getattr(dev_resume, "front_end", None)
        back= dev_resume.get("back_end") if isinstance(dev_resume, dict) else getattr(dev_resume, "back_end", None)
        database= dev_resume.get("databases") if isinstance(dev_resume, dict) else getattr(dev_resume, "databases", None) 
        cloud= dev_resume.get("clouds") if isinstance(dev_resume, dict) else getattr(dev_resume, "clouds", None) 
        work= dev_resume.get("works") if isinstance(dev_resume, dict) else getattr(dev_resume, "works", None)
        proj= dev_resume.get("projects") if isinstance(dev_resume, dict) else getattr(dev_resume, "projects", None)

        print()
        return helper.templates.TemplateResponse("modal_portfolio.html", {"request": request, 'user_in': cur_emp, "dev": dev_found, "edu": edu, 
                                                                        "cert": cert, "front": front, "back": back, 
                                                                        "databases": database, "clouds": cloud, "works": work, "proj": proj})
    else:
        return await helper.login_expired()



# function to update developer portfolio
@restrict_api.post('/update_portfolio', include_in_schema= False)
async def update_portfolio(request: Request, db: Session= Depends(get_db), 
                        cur_user: Developer= Depends(get_current_user)):
    if cur_user:
        result= await portfolio_dao.update_portfolio(await request.form(), cur_user.Id, db)
        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await helper.login_expired()



# function to update developer ocupation
@restrict_api.post('/update_ocupation', include_in_schema= False)
async def update_ocupation(request: Request, db: Session= Depends(get_db), 
                      cur_user: Developer= Depends(get_current_user)):
    
    if cur_user:
        result= await developers_dao.update_ocupation(await request.form(), cur_user.Id, db)
        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await helper.login_expired()
    


# function to update developer coding level
@restrict_api.post('/update_code_level', include_in_schema= True)
async def update_code_level(request: Request, db: Session= Depends(get_db), 
                      cur_user: Developer= Depends(get_current_user)):
    
    if cur_user:
        result= await developers_dao.update_coding_level(cur_user, await request.form(), db)
        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await helper.login_expired()



# function to update developer password
@restrict_api.post('/dev_account/update_developer_password', status_code=status.HTTP_200_OK)
@limiter.limit("3/day") # limit 3 update password per hour
async def update_developer_password(request: Request, bg_tast: BackgroundTasks, db: Session= Depends(get_db),
                          cur_user: Developer= Depends(get_current_user)):
    # check if developer is loged in
    if cur_user:
        # update developer password
        result= await developers_dao.developer_update_password(cur_user, await request.form(), bg_tast, db)
        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await helper.login_expired()
    
    

# function to list all jobs a developer applied
@restrict_api.get('/jobs applied', include_in_schema= False)
async def my_applications(request: Request, page: int= 1, db: Session= Depends(get_db),
                          cur_dev: Developer= Depends(get_current_user)):
    if cur_dev:
        result= await jobs_dao.list_all_jobs_dev_application(cur_dev, db)
        return helper.templates.TemplateResponse("jobs_applied.html", {'request': request, 'result': result, 'user_in': cur_dev})
    else:
        return await helper.login_expired()
  


# function to display HTML page and user data
@restrict_api.get('/dev_account')
async def dev_account(request: Request, cur_user: Developer= Depends(get_current_user), 
                   db: Session= Depends(get_db)):

    if cur_user:
        result= None
        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await helper.login_expired()



# function to deactivate developer account
@restrict_api.post('/', include_in_schema= False)
async def deactivate_account(request: Request, bg_task: BackgroundTasks, db: Session= Depends(get_db), 
                            cur_user: Developer= Depends(get_current_user)):
    if cur_user:
        result= await developers_dao.deactivate(cur_user, bg_task, db)
        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await login_expired(request, db)



# function to delete an developer account
@restrict_api.delete('/delete_developer_account')
async def delete_developer(request: Request, user_email: str, db: Session= Depends(get_db), 
                           cur_user: Developer= Depends(get_current_user)):

    if cur_user:
        if cur_user.Email == user_email:
            return developers_dao.delete(cur_user, db)
        else:
            return http_responses.status_406_not_acceptable("bi bi-envelope-x-fill", f"Account: {user_email} does not match the user loged-in!")
    else:
        return await helper.login_expired()



# function to update profile image
@restrict_api.post('/update_profile_image/', status_code=status.HTTP_202_ACCEPTED, include_in_schema=True)
@limiter.limit("3/day") # limit 3 update profile image per hour
async def update_profile_image(request: Request, file: UploadFile, cur_dev: Developer= Depends(get_current_user),
                            db: Session= Depends(get_db)):
    if cur_dev:
        response= await helper.process_img(image_utils.DEV_IMG_DIR, file, cur_dev, db)

        if response:
            result= http_responses.status_200_ok("bi bi-person-badge-fill", "Profile image successfully updated")
        else:
            result= response 
        return await load_my_dev_account(request, result, cur_dev, db)
    else:
        return await helper.login_expired()
    


# function to delete profile image
@restrict_api.post('/delete_profile_image/{user_id}', status_code=status.HTTP_200_OK, include_in_schema=True)
async def delete_profile_image(request: Request, user_id: uuid.UUID, cur_user: Developer= Depends(get_current_user),
                            db: Session= Depends(get_db)):
    if cur_user:
        if cur_user.Id != user_id:
            result= http_responses.status_403_forbidden("bi bi-image", "You're not authorized to update this profile picture!")
            
        elif not cur_user.Image:
            result= http_responses.status_404_not_found("bi bi-exclamation-circle-fill", "Profile picture not available!")
           
        else:
            result = await developers_dao.delet_profile_picture(cur_user, db)

        return await load_my_dev_account(request, result, cur_user, db)
    else:
        return await helper.login_expired()