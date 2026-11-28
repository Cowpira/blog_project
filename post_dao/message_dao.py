from sqlalchemy.orm import aliased, joinedload, selectinload, Session
from datetime import datetime, timezone
from sqlalchemy import and_, exists, func, select, delete, or_
from data_model.models import Message, Person, Developer 
from services import http_responses, helper


# function to increase person totals messages
def add_total_messages(user, db: Session):
    # find the user and updated the total of messages
    user_query= select(Person).where(Person.Id == user.Id)
    user_found= db.execute(user_query).scalar()

    if user_found:
        user_found.Total_Messages += 1
    
    db.add(user_found)
    db.commit()



# function to decrease person total messages
def subtract_total_msg(user_in, db: Session):
    # find the user and updated the total of messages
    user_query= select(Person).where(Person.Id == user_in.Id)
    user_found= db.execute(user_query).scalar()

    if user_found and user_found.Total_Messages > 0:
        user_found.Total_Messages -= 1

        db.add(user_found)
        db.commit()
        db.refresh(user_found)



# function to set message as viewed
async def update_msg_viwed(user_in, msg_id, db: Session):
    msg_query= select(Message).where(Message.Id == msg_id)
    msg_found= db.execute(msg_query).scalar()
    was_updated= False

    if msg_found:
        # cehck if msg is unred and msg recepient
        if msg_found.Viewed == 0 and msg_found.To == user_in.Id:
            msg_found.Viewed= 1
            was_updated= True

        # msg thread: sort all messages by sent date, and check last reply to
        elif msg_found.replies:
            unread_replies= False

            for reply in msg_found.replies:
                if reply.To == user_in.Id and reply.Viewed == 0:
                    reply.Viewed=1
                    unread_replies= True
                
            if unread_replies:
                msg_found.Viewed= 1
                was_updated= True

        # call function to descrease total of messages an user have
        if was_updated:
            db.commit()
            subtract_total_msg(user_in, db)


        
# function to list all messages to the employee or user online
async def list_messages(user_id, msg_by, page, total_items, db: Session):
    ReplyDateAlias= aliased(Message)

    # subquery to get all latest reply date in a message chat thread
    latest_replies_subq= (select(
        func.max(ReplyDateAlias.Created))
        .where(ReplyDateAlias.Parent_Id == Message.Id)
        .correlate(Message)
        .scalar_subquery()
    )

    # sort by newest reply date if replies exist, otherwise by message Created Date
    latest_activity= func.coalesce(latest_replies_subq, Message.Created)

    if msg_by == 'chats':
        query= (select(Message)
            .where(
                Message.Parent_Id.is_(None),
                Message.replies.any(), 
                or_(Message.Person_Id == user_id, Message.To == user_id),
            )
        )
    elif msg_by == 'employee':
        query= (select(Message).join(Person, Message.Person_Id == Person.Id)
            .where(
                Message.To == user_id,
                Message.Parent_Id.is_(None),
                Person.Type == 'employeer',
            )
        )
    elif msg_by == 'unread':
        UnreadReply= aliased(Message)
        has_unread_reply= exists(
            select(UnreadReply.Id).where(
                UnreadReply.Parent_Id == Message.Id,
                UnreadReply.To == user_id,
                UnreadReply.Viewed == False,
            )
        )
        query= (select(Message)
            .where(Message.Parent_Id.is_(None), 
                or_(
                    and_(Message.To == user_id, Message.Viewed == False),
                    has_unread_reply,
                ),
            )
        )
    elif msg_by== 'dev':
        Reply= aliased(Message)
        ReplySender= aliased(Person)

        has_dev_reply= exists(
            select(Reply.Id)
            .join(ReplySender, Reply.Person_Id == ReplySender.Id)
            .where(
                Reply.Parent_Id == Message.Id, 
                Reply.To == user_id, 
                ReplySender.Type == 'developer',
            )
        )
        query= (
            select(Message)
            .outerjoin(Person, Message.Person_Id == Person.Id)
            .where(Message.Parent_Id.is_(None),
                   or_(
                       and_(Message.To == user_id, Person.Type == 'developer'),
                       and_(Message.Person_Id == user_id, has_dev_reply),
                ),
            )
        )
    else:
        query= select(Message).where(
            Message.Parent_Id.is_(None),
            or_(Message.Person_Id == user_id, Message.To == user_id),
        )

    # attach latest reply, eager load replies, sort newest activity first
    query= (query.options(
            joinedload(Message.msg_sender),
            selectinload(Message.replies).joinedload(Message.msg_sender),
        ).order_by(latest_activity.desc(), Message.Id.desc())
    )

    # getting messages data set
    data_set= helper.global_data_pagination(query, page, total_items, db)
    return data_set



# function to save message when developer answer or reply a post
async def send_message(msg, sender, msg_id, msg_to, parent_id, system, db: Session):
    try:
        new_msg= Message(
            Message_Content= msg,
            Created= datetime.now(timezone.utc),
            System_Message= system,
            Viewed= 0,
            To= msg_to,
            Person_Id= None if sender == 'FP System' else sender.Id,
            Parent_Id= parent_id if parent_id > 0 else msg_id 
        )

        query= select(Developer.First_Name).filter(Developer.Id == msg_to)
        receiver= db.execute(query).scalar()

        db.add(new_msg)
        db.commit()

        # update total message a user have
        user_query= select(Person).where(Person.Id == msg_to)
        user_found= db.execute(user_query).scalar()
        add_total_messages(user_found, db)

        return http_responses.status_200_ok("bi bi-send-check-fill", f"Message succesfully sent to {receiver}")
    
    except SystemError as sys_error:
        return http_responses.status_200_ok("bi bi-send-check-fill", f"Count not reply. Error {sys_error}")



# function to save message when developer answer or reply a post
async def reply_message(msg, user_in, msg_id, msg_to, system, db: Session):
    try:
        # fetch parent msg to check unread state
        query= select(Message).where(Message.Id == msg_id)
        parent_msg= db.execute(query).scalar_one_or_none()

        sender_unread= False
        recepient_unread= False

        if parent_msg:
            # cehck if user in has unread msg/reply in a thread
            if parent_msg.Viewed == 0 and parent_msg.To == user_in.Id:
                sender_unread= True
            elif parent_msg.replies:
                last_reply= max(parent_msg.replies, key= lambda r: r.Created)

                if last_reply.To == user_in.Id and last_reply.Viewed == 0:
                    sender_unread= True
                elif last_reply.To == msg_to and last_reply.Viewed == 0:
                    # recepient alredy have unread msg reply in a thread
                    recepient_unread= True

            if parent_msg.Viewed == 0 and parent_msg.To == msg_to:
                recepient_unread= True


            parent_msg.Viewed= 2
            for reply in parent_msg.replies:
                if reply.To == user_in.Id and reply.Viewed == 0:
                    reply.Viewed= 1

        # save new reply 
        new_msg= Message(
            Message_Content= msg,
            Created= datetime.now(timezone.utc),
            System_Message= system,
            Viewed= 0,
            To= msg_to,
            Person_Id= user_in.Id,
            Parent_Id= msg_id
        )

        if parent_msg:
            parent_msg.Viewed = 2

        db.add(new_msg)
        db.commit()

        # subtract one from total msg if a user in already replied a unread msg thread
        if sender_unread:
            subtract_total_msg(user_in, db)

        # add 1 to total msg a recepient have, if they dont have unread msg in a thread
        if not recepient_unread:
            recep_query= select(Person).where(Person.Id == msg_to)
            recep_found= db.execute(recep_query).scalar()
            if recep_found:
                add_total_messages(recep_found, db)


        # setting this message parent ID so we can track as chat
        target_parent_id= msg_id
        query= select(Message).where(Message.Id == target_parent_id)
        parent_msg= db.execute(query).scalar_one_or_none()

        return http_responses.status_200_ok("bi bi-send-check-fill", f"{user_in.First_Name} your reply was sent")
    
    except SystemError as sys_error:
        return http_responses.status_200_ok("bi bi-send-check-fill", f"Count not reply. Error {sys_error}")



# count how many chats a user are participating
async def count_chats(user_id, db: Session):
    Reply= aliased(Message)

    unread_replies= exists(
        select(Reply.Id).where(
            Reply.Parent_Id == Message.Id, 
            Reply.To == user_id, 
            Reply.Viewed == 0)
    )

    query= select(func.count(Message.Id)) \
        .where(Message.Parent_Id.is_(None), or_(Message.Person_Id == user_id, Message.To == user_id), \
            unread_replies,
        )
    return db.scalar(query) or 0

 

# function to delete a message by id
async def delete_message_by_id(msg_id, user_in, db: Session):
    try:
        query= delete(Message).where(Message.Id == msg_id)
        add_total_messages(user_in, db)
        
        db.execute(query)
        db.commit()

        # call function to descrease total of messages an user have
        subtract_total_msg(user_in, db) 

        return http_responses.status_200_ok("bi bi-chat-square", f"Message with ID:{msg_id} was deleted")
    
    except SystemError as sys_error:
        return sys_error