from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from data_model.models import Response, Answer
from services import http_responses
from post_dao import message_dao


# method to list all responses
def list_replies(db: Session):
    query=  db.execute(select(Response))

    if query:
        return query.scalars().all()
    else:
        return False
    


# method to list all responses by post ID
async def replies_by_post_id(post_id, db: Session):
    # query= select(Response).where(Response.post_id == post_id)
    # responses_found= db.execute(query).scalars().all()
    query= select(Response).join(Answer, Response.answer_id == Answer.Id).where(Answer.post_id == post_id)
    responses_found= db.execute(query).scalars().all() 
    if responses_found:
        return responses_found
    else:
        return False



#You responded this answer. Consider editing your respond instead!
# function to add new answer
async def reply_to_answer(url_for, answer_id, post_id, data, developer, db: Session):
    query= select(Response).where(Response.answer_id == answer_id and Response.dev_id == developer.Id)
    reply_found= db.execute(query).scalar()
    
    # check if current developer already replied  
    if reply_found:
        return http_responses.status_406_not_acceptable("bi bi-exclamation-circle-fill", 
                                                        f"Sorry, {developer.First_Name}. You have already replied this answer!")
    else:
        new_response = Response(
            Tag= data.get("answer_tags"),
            Response= data.get('replying_answer'),
            Posted= datetime.now(timezone.utc),
            answer_id= answer_id,
            dev_id= developer.Id
        )

        db.add(new_response)
        db.commit()
        db.refresh(new_response)

        # after save developer reply we send a message for the developer who answered 
        answer_query= select(Answer).where(Answer.Id == answer_id)
        answer_found= db.execute(answer_query).scalar()

        # send a message to notify the answer got a reply and update messge count budged
        if answer_found:
            reply_link= url_for("view_post", post_id=post_id)
            msg= f'{answer_found.write_answer.First_Name} your answer was replied by {developer.First_Name}. <br>\
                <div class="row ms-1">To view the reply click: <a class="col-12 fp-links nav-link" href="{reply_link}"> View Reply </a></div>'

            await message_dao.send_message(msg, 'FP System', answer_id, answer_found.Id, 0, True, db)
            await message_dao.update_total_messages(answer_found, db)


        return http_responses.status_200_ok("bi bi-repeat-1", f"Thanks {developer.First_Name} for replying an answer")
        


# method to edit a response
async def edit_reply(reply_id, data, db: Session):
    query= select(Response).where(Response.Id == reply_id)
    reply_found= db.execute(query).scalar()

    if reply_found:
        reply_found.Tag= data.get("edit_reply_tags") or ""
        reply_found.Response= data.get("edit_reply")
        reply_found.Posted= datetime.now(timezone.utc)

        db.add(reply_found)
        db.commit()
        db.refresh(reply_found)

        return http_responses.status_200_ok("bi bi-check2-circle", "You successfully updated your response")
    else:
        return http_responses.status_404_not_found("bi bi-database-exclamation", "We could not find this reply to update it. Try again!")