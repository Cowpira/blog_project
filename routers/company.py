from fastapi import APIRouter, Depends, UploadFile, Request
from post_dao import company_dao
from services import db_connection, authentication
from routers.employeer import load_eployeer_Account
from routers.login import limiter
from data_model.models import Employee
from sqlalchemy.orm import Session
from typing import Annotated


restrict_api= APIRouter()  # authenticated router


# function to add new company
@restrict_api.post('/add_company', include_in_schema=False)
@limiter.limit("5/hour") # limit add 5 new jobs per hour
async def add_company(request: Request, file: UploadFile, db: Annotated[Session, Depends(db_connection.get_db)],
                    cur_employee: Employee= Depends(authentication.get_current_user)):
    
    if cur_employee:
        result= await company_dao.add_new_company(file, await request.form(), cur_employee, db)
        return await load_eployeer_Account(request, result, cur_employee, db)
    else:
        return await globals.login_expired()
    


# function to update company
@restrict_api.post('/update_company', include_in_schema=False)
@limiter.limit("10/hour") # limit 5 update jobs per hour
async def update_company(request: Request, file: UploadFile, db: Annotated[Session, Depends(db_connection.get_db)],
                        cur_employee: Employee= Depends(authentication.get_current_user)):
    if cur_employee:
        result= await company_dao.update_company(file, await request.form(), cur_employee, db)
        return await load_eployeer_Account(request, result, cur_employee, db)
    else:
        return await globals.login_expired()