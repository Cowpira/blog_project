import uuid

from fastapi import APIRouter, Depends, Request, status
from post_dao import answer_dao
from data_model.models import Developer
from services.helper import login_expired
from services.db_connection import get_db
from services.authentication import get_current_user
from routers.post import load_post_view_content
from routers.login import limiter
from sqlalchemy.orm import Session


restrict_api= APIRouter()  # router for authenticated users


##############################################################################################################################
################################ RESTRICTED FUNCTIONS FOR LOGGED IN DEVELOPERS OR EMPLOYEERS  ################################

# method to add answer for a post
@restrict_api.post('/answer_post/{post_id}', status_code=status.HTTP_200_OK, include_in_schema= False)
@limiter.limit("2/hour") # limit 8 answer per hour
async def answer_post(post_id: uuid.UUID, request: Request, cur_user: Developer= Depends(get_current_user), 
                      db: Session= Depends(get_db)):
    
    if cur_user:
        result= await answer_dao.answer_post(post_id, await request.form(), cur_user, db)
        # call function load post from ROUTERS -> POST
        return await load_post_view_content(request, post_id, result, cur_user, db)
    else:
        return await login_expired()

    

# method to edit a answer
@restrict_api.post('/update_answer/{answer_id}&{post_id}', status_code=status.HTTP_200_OK, include_in_schema= False)
@limiter.limit("5/hour") # limit update 5 answer per hour
async def update_answer(answer_id: uuid.UUID | int, post_id: uuid.UUID | int, request: Request, 
                        cur_user: Developer= Depends(get_current_user), 
                        db: Session= Depends(get_db)):
    if cur_user:
        result= await answer_dao.edit_answer(answer_id, await request.form(), db)
        return await load_post_view_content(request, post_id, result, cur_user, db)
    else:
        return await login_expired()