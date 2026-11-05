from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, status, Request
from post_dao import employee_dao, company_dao
from services import helper, db_connection, authentication
from routers.login import limiter
from data_model.models import Employee
from data_model.schemas import Employeer_Response
from sqlalchemy.orm import Session
from typing import Annotated


public_api= APIRouter() # public router
restrict_api= APIRouter()  # authenticated router

# function to load employeer data
async def load_eployeer_Account(request, result, cur_employee, db):
    company= await company_dao.get_company(cur_employee.Id, db)
    return helper.templates.TemplateResponse("my_employee_account.html", {'request': request, 'user_in': cur_employee, 'result': result, 
                                                                        'company': company, 'today': datetime.now(timezone.utc)})


##############################################################################################################################
############################################### PUBLIC FUNCTIONS FOR ALL USERS  ##############################################

# function to display HTML page form and get employeer data
@public_api.get('', include_in_schema= False)
async def add_employeer(request: Request):
    return helper.templates.TemplateResponse('create_employeer_account.html', {'request': request, 'result': "", 'data': ""})


# function to add new employeer
@public_api.post('', response_model=Employeer_Response, status_code=status.HTTP_200_OK, include_in_schema= True)
@limiter.limit("2/day") # limit create 2 employee account per day
async def add_employeer(request: Request, bg_task: BackgroundTasks, db: Annotated[Session, Depends(db_connection.get_db)]):
    result= await employee_dao.create_employeer(await request.form(), request.url_for, db, bg_task)
     
    if result.status_code == 200:
        developers= await helper.get_top_developers(db)
        return helper.templates.TemplateResponse('index.html', context= {'request': request, 'user_in': '', 'result': result, 'users': developers})
    else:
        return helper.templates.TemplateResponse("create_employeer_account.html", 
                                                {'request': request, 'result': result, 'data': await request.form()})



################################################################################################################
################################ RESTRICTED FUNCTIONS FOR LOGGED IN EMPLOYEERS  ################################
 
# function to show employee account details
@restrict_api.get('/employeer_account')
async def employee_account(request: Request, db: Annotated[Session, Depends(db_connection.get_db)],
    cur_employee: Employee= Depends(authentication.get_current_user)):

    if cur_employee:
        return await load_eployeer_Account(request, '', cur_employee, db)
    else:
        return await helper.login_expired()



# function to update employee data
@restrict_api.post('/update_employee_data', include_in_schema=False, response_model=Employeer_Response)
@limiter.limit("5/hour") # limit 5 update employee data per hour
async def update_employee_data(request: Request, db: Annotated[Session, Depends(db_connection.get_db)], 
                        cur_employee: Employee= Depends(authentication.get_current_user)):
    
    if cur_employee:
        result= await employee_dao.update_employeer(await request.form(), cur_employee, db)
        return await load_eployeer_Account(request, result, cur_employee, db)
    else:
        return await helper.login_expired()



# function to update emloyeer password
@restrict_api.post('/employeer_account/update_employeer_password', include_in_schema= False)
@limiter.limit("3/day") # limit 3 update password per day
async def update_employeer_password(request: Request, db: Annotated[Session, Depends(db_connection.get_db)], 
        cur_employee: Employee= Depends(authentication.get_current_user)):
    
    if cur_employee:
        result= await employee_dao.employeer_update_password(cur_employee, await request.form(), db)

        return await load_eployeer_Account(request, result, cur_employee, db)
    else:
        return await helper.login_expired()
