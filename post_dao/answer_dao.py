from datetime import datetime, timezone
from sqlalchemy import select
from data_model.models import Answer, Post
from services import http_responses
from sqlalchemy.orm import Session


# method to list all answers
def list_answers(db: Session):
    query= db.execute(select(Post))

    if query:
        return query.scalars().all()
    else:
        return False




# method to list all answers by a post ID
async def answers_by_post_id(post_id, db: Session):
    query= select(Answer).where(Answer.post_id == post_id)
    answers_found= db.execute(query).scalars().all()

    if answers_found:
        return answers_found
    else:
        return None




#You answered this post. Consider editing your answer instead!
# method to add new answer
async def answer_post(post_id, answer, user, db: Session):
    query= db.execute(select(Answer).where(Answer.post_id == post_id, Answer.dev_id == user.Id))    
    answer_found= query.scalar()

    if answer_found:
        return http_responses.status_406_not_acceptable("bi bi-exclamation-diamond-fill", 
                                                        f"Sorry {user.First_Name} you have already answered! <br> Consider editing your previous answer")
    else:
        new_answer= Answer(
            Tag= answer.get("answer_tags"),
            Answer= answer.get("answer_post"),
            Posted= datetime.now(timezone.utc),
            post_id= post_id,
            dev_id= user.Id
        )

        # if an answer is added to a post we update post total answer
        post_query= db.execute(select(Post).where(Post.Id == post_id))
        post_found= post_query.scalar()
        
        if post_found:
            post_found.Total_Answer += 1
    
        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)

        return http_responses.status_200_ok("bi bi-chat-square-dots", f"{user.First_Name} you successfully answered")
    


# method to add new answer
async def edit_answer(answer_id, answer, db: Session):
    answer_found= db.query(Answer).filter(Answer.Id == answer_id).first()

    if answer_found:
        answer_found.Tag= answer.get("edit_answer_tags")
        answer_found.Answer= answer.get("edit_answer")
        answer_found.Posted= datetime.now(timezone.utc)

        db.commit()
        return http_responses.status_200_ok("bi bi-chat-square-dots", "Answer successfully updated")
    else:
        return http_responses.status_404_not_found("bi bi-body-text", "The answer you tried to edit was not found!")