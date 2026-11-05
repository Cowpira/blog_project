from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from sqlalchemy import func, select, delete, or_
from data_model.models import Message, Person, Developer
from sqlalchemy.orm import Session    
from services import http_responses


# function to increase person totals messages
async def update_total_messages(developer, db: Session):
    try:
        # update user loged in total messages 
        query = select(Message).where(Message.To == developer.Id, Message.Viewed == False, Message.Parent_Id == None)
        developer.Total_Messages= len(db.execute(query).scalars().all())
       
        db.add(developer)
        db.commit()
        db.refresh(developer)
       
    except ValueError:
        return f'Could not update total of messages for the user {developer.First_Name}!'



# function to decrease person total messages
def subtract_total_msg(user_in, db: Session):
        # find the user and updated the total of messages
        user_query= select(Person).where(Person.Id == user_in.Id)
        user_found= db.execute(user_query).scalar()

        if user_found:
            user_found.Total_Messages -= 1

            db.add(user_found)
            db.commit()
            db.refresh(user_found)



# function to set message as viewed
async def update_msg_viwed(user_in, msg_id, db: Session):
    msg_query= select(Message).where(Message.Id == msg_id)
    msg_found= db.execute(msg_query).scalar()

    if msg_found and not msg_found.Viewed:
        msg_found.Viewed= True

        db.add(msg_found)
        db.commit()
        db.refresh(msg_found)

        # call function to descrease total of messages an user have
        subtract_total_msg(user_in, db)



# count how many chats a user are participating
async def count_chats(user_id, db: Session):
    query= select(func.count(Message.Id)).where(Message.Viewed == False, Message.replies.any()) \
            .where(or_(Message.Person_Id == user_id, Message.To == user_id))

    return db.scalar(query)


        
# function to list all messages to the employee or user online
async def list_messages(user_id, msg_by, db: Session):
    
    if msg_by == 'chats':
        query= select(Message).where(Message.replies.any()) \
            .where(or_(Message.Person_Id == user_id, Message.To == user_id)) \
            .options(selectinload(Message.replies)).order_by(Message.Send_Date.desc())
        msg= "You have not chat yet!"

    elif msg_by == 'all':
        query= select(Message).where(Message.Parent_Id.is_(None), \
            or_(Message.Person_Id == user_id, Message.To == user_id)) \
            .options(selectinload(Message.replies)).order_by(Message.Send_Date.desc())
        msg= "There is no message for you!"

    elif msg_by == 'sys':
        query= select(Message).where(Message.To == user_id, Message.Parent_Id.is_(None), Message.System_Message == True) \
            .options(selectinload(Message.replies)).order_by(Message.Send_Date.desc())
        msg= "You have no message from <br> Future Programmers"

    elif msg_by == 'unread':
        query= select(Message).where(Message.To == user_id, Message.Parent_Id.is_(None), Message.Viewed == False) \
            .options(selectinload(Message.replies)).order_by(Message.Send_Date.desc())
        msg= "You have no unread message!"
    
    else:
        query= select(Message).where(Message.To == user_id, Message.Parent_Id.is_(None), Message.System_Message == False) \
            .options(selectinload(Message.replies)).order_by(Message.Send_Date.desc())
        msg= "You have no message from any <br> Developers or Employeer!"

        
    # getting a list of messages
    messages= db.scalars(query).all()

    if messages:
        return messages
    else:
        return http_responses.status_204_no_content("bi bi-chat-square-text", msg)



# function to save message when developer answer or reply a post
async def send_message(msg, sender, msg_id, msg_to, parent_id, system, db: Session):
    try:
        new_msg= Message(
            Message_Content= msg,
            Send_Date= datetime.now(timezone.utc),
            System_Message= system,
            Viewed= False,
            To= msg_to,
            Person_Id= None if sender == 'FP System' else sender.Id,
            Parent_Id= parent_id if parent_id > 0 else msg_id 
        )

        query= select(Developer.First_Name).filter(Developer.Id == msg_to)
        receiver= db.execute(query).scalar()

        db.add(new_msg)
        db.commit()
        return http_responses.status_200_ok("bi bi-send-check-fill", f"Message succesfully sent to {receiver}")
    
    except SystemError as sys_error:
        return http_responses.status_200_ok("bi bi-send-check-fill", f"Count not reply. Error {sys_error}")



# function to save message when developer answer or reply a post
async def reply_message(msg, user_in, msg_id, msg_to, parent_id, system, db: Session):
    try:
        # save rely as new message 
        new_msg= Message(
            Message_Content= msg,
            Send_Date= datetime.now(timezone.utc),
            System_Message= system,
            Viewed= True,
            To= msg_to,
            Person_Id= user_in.Id,
            Parent_Id= parent_id
        )

        db.add(new_msg)
        db.commit()

        # setting this message parent ID so we can track as chat
        query= select(Message).where(Message.Id == msg_id)
        parent_msg= db.execute(query).scalar()

        if parent_msg:
            parent_msg.Viewed = True

            db.add(parent_msg)
            db.commit()

        # call function to descrease total of messages an user have
        subtract_total_msg(user_in, db) 
        return http_responses.status_200_ok("bi bi-send-check-fill", f"{user_in.First_Name} your reply was sent")
    
    except SystemError as sys_error:
        return http_responses.status_200_ok("bi bi-send-check-fill", f"Count not reply. Error {sys_error}")

    

# function to delete a message by id
async def delete_message_by_id(msg_id, user_in, db: Session):
    try:
        query= delete(Message).where(Message.To == user_in.Id, Message.Id == msg_id)

        await update_total_messages(user_in, db)
        
        db.execute(query)
        db.commit()

        # call function to descrease total of messages an user have
        subtract_total_msg(user_in, db) 

        return http_responses.status_200_ok("bi bi-chat-square", f"Message with ID:{msg_id} was deleted")
    
    except SystemError as sys_error:
        return sys_error