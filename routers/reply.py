import uuid

from fastapi import APIRouter, Depends, Request, status
from post_dao import reply_dao
from data_model.models import Developer
from services.helper import login_expired
from services.db_connection import get_db
from services.authentication import get_current_user
from sqlalchemy.orm import Session
from routers.post import load_post_view_content
from routers.login import limiter


restrict_api= APIRouter()  # router for authenticated users

##############################################################################################################################
####################################### RESTRICTED FUNCTIONS FOR LOGGED IN DEVELOPERS  #######################################

# function to add response to answer
@restrict_api.post('/reply_answer/{answer_id}&{post_id}', include_in_schema= False, status_code=status.HTTP_200_OK)
@limiter.limit("25/hour") # limit 5 reply answer request per hour
async def reply_answer(answer_id: uuid.UUID | int, post_id: uuid.UUID | int, request: Request, 
                       cur_user: Developer= Depends(get_current_user), db: Session= Depends(get_db)):
    if cur_user:
        result= await reply_dao.reply_to_answer(request.url_for, answer_id, post_id, await request.form(), cur_user, db)
        return await load_post_view_content(request, post_id, result, cur_user, db)
    else:
        return await login_expired()



# function to edit a response
@restrict_api.post('/update_reply/{reply_id}&{post_id}', status_code=status.HTTP_200_OK, include_in_schema= False)
@limiter.limit("3/hour") # limit 3 update reply request per hour
async def update_reply(post_id: uuid.UUID | int, reply_id: uuid.UUID | int, request: Request, 
                       cur_user: Developer= Depends(get_current_user), db: Session= Depends(get_db)):
    if cur_user:
        result= await reply_dao.edit_reply(reply_id, await request.form(), db)
        return await load_post_view_content(request, post_id, result, cur_user, db)
    else:
        return await login_expired()