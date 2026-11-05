import uuid

from post_dao import message_dao
from data_model.models import Developer, Employee, Person
from services import helper
from services.authentication import get_current_user
from services.db_connection import get_db
from routers.developers import developers_page_destination
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from data_model.models import Person
from sqlalchemy.orm import Session  


restrict_api= APIRouter()  # router for authenticated users


async def load_messages(request, msg, cur_user, page, msg_by, db):
    result= None
    paginated_messages= None
    # list all messages for current user online
    data= await message_dao.list_messages(cur_user.Id, msg_by, db)
    
    if type(data) is list:
        paginated_messages= helper.pagination_settings(data, page, 'messages', 3)
        result= msg
    else:
        result= data
    return helper.templates.TemplateResponse("my_messages.html", {'request': request, 'user_in': cur_user, 'result': result, 'msg_by': msg_by, 
                                                                    'my_messages': paginated_messages, 'tot_chats': await message_dao.count_chats(cur_user.Id, db)})


##############################################################################################################################
################################ RESTRICTED FUNCTIONS FOR LOGGED IN DEVELOPERS OR EMPLOYEERS  ################################

# function to get developer or employee messages
@restrict_api.get('/my_messages/{page}&{list}&{msg_by}', include_in_schema= False)
async def my_messages(request: Request, msg_by: str, page: int= 1, cur_user: Developer= Depends(get_current_user),
                    db: Session= Depends(get_db)):
    if cur_user:
        return await load_messages(request, '', cur_user, page, msg_by, db)
    else:
        return await helper.login_expired()



# function to send a message
@restrict_api.post('/new_message/{msg_to}', include_in_schema= False)
async def new_message(request: Request, msg_to: uuid.UUID, cur_user: Person= Depends(get_current_user),
                       db: Session= Depends(get_db)):
    if cur_user:
        data= await request.form()
        result= await message_dao.send_message(data.get("msg_to_send"), cur_user, None, msg_to, 0, False, db)

        return await developers_page_destination(request, None, 1, helper.total_items, cur_user, result, db)
    else:
        return await helper.login_expired()



# function to reply a message
@restrict_api.post('/reply_msg/{msg_id}&{msg_to}&{msg_by}', include_in_schema= False)
async def reply_msg(request: Request, msg_id: uuid.UUID, msg_to: uuid.UUID, msg_by: str, 
                    cur_user: Developer= Depends(get_current_user), db: Session= Depends(get_db)):
    
    if cur_user:
        parent_id= msg_id
        data= await request.form()
        result= await message_dao.reply_message(data.get("reply_msg"), cur_user, msg_id, msg_to, parent_id, False, db)

        return await load_messages(request, result, cur_user, 1, msg_by, db)
    else:
        return await helper.login_expired()



# function to subtract 1 from the total messages and update message viewed as True
@restrict_api.get('/msg_viewed/{msg_id}&{msg_by}', include_in_schema=False)
async def msg_viewed(request: Request, msg_by: str, msg_id: uuid.UUID, db: Session= Depends(get_db), 
                                  cur_user: Person= Depends(get_current_user)):
    if cur_user:
        # call function to subtract total messages and mark message as viewed
        await message_dao.update_msg_viwed(cur_user, msg_id, db)
        return await load_messages(request, '', cur_user, 1, msg_by, db)
    else:
        return await helper.login_expired() 



# function to delete a message
@restrict_api.get('/delete_message/{msg_id}&{msg_by}', include_in_schema=False)
async def delete_message(request: Request, msg_by: str, msg_id: uuid.UUID, db: Session= Depends(get_db), 
                         cur_user: Person= Depends(get_current_user)):

    if cur_user:
        # call function to delete a message
        response= await message_dao.delete_message_by_id(msg_id, cur_user, db)
        return await load_messages(request, response, cur_user, 1, msg_by, db)
    else:
        return await helper.login_expired()



# function to send email to a developer through his/her resume modal
@restrict_api.post('email_to_dev/{emp_id}&{dev_id}', include_in_schema=False)
async def email_to_dev(request: Request, emp_id: int, dev_id: int, db: Session= Depends(get_db), 
                       cur_user: Employee= Depends(get_current_user)):
    pass
